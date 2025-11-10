import io
import calendar
from datetime import date, timedelta
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from login.models import Usuario
from warehouse.models import Inventory, Movement
from application.models import ApplicationDetail
from reports.pdf_reportlab import generar_pdf_reportlab  
from django.db.models import Sum
from io import BytesIO
from twilio.rest import Client

EMAIL_FROM = settings.EMAIL_HOST_USER

# =========================================================
# 🔹 FUNCIONES AUXILIARES
# =========================================================

def get_month_date_range(reference_date=None):
    """Retorna el primer y último día del mes actual."""
    today = reference_date or date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return first_day, last_day


def get_last_business_day(today=None):
    """
    Retorna True si hoy es el último día hábil del mes.
    (Si el último día cae sábado o domingo, se ajusta al viernes anterior)
    """
    today = today or date.today()
    _, last_day = get_month_date_range(today)
    while last_day.weekday() >= 5:  # 5=sábado, 6=domingo
        last_day -= timedelta(days=1)
    return today == last_day


# =========================================================
# 🔹 ALERTAS DE STOCK BAJO
# =========================================================

def send_low_stock_alert(threshold=100):
    """Envía correo y mensaje de WhatsApp si hay productos con bajo stock."""

    # 1️⃣ Buscar productos con stock bajo
    low_stock_items = Inventory.objects.filter(
        warehouse__type__in=['shed', 'main'],
        quantity_packages__lte=threshold
    ).select_related('warehouse', 'product')

    if not low_stock_items.exists():
        print("No hay productos con bajo stock. ✅")
        return

    # 2️⃣ Obtener casetas afectadas
    casetas_afectadas = sorted(set(item.warehouse.name_ware for item in low_stock_items))

    # 3️⃣ Enviar correo a administradores
    admins = Usuario.objects.filter(
        roles__name_role="Administrador",
        correo__isnull=False
    ).distinct()

    for admin in admins:
        html_content = render_to_string(
            'notification/low_stock_alert.html',
            {'low_stock_items': low_stock_items, 'admin_name': admin.nombre_usuario}
        )
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject="⚠️ Alerta de Stock Bajo",
            body=text_content,
            from_email=EMAIL_FROM,
            to=[admin.correo],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        print(f"📧 Correo enviado a {admin.nombre_usuario} ({admin.correo})")

    # 4️⃣ Enviar resumen por WhatsApp
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    resumen_msg = (
        " *Alerta de Stock Bajo* \n\n"
        "Tienes productos con stock bajo en las siguientes casetas:\n"
        + "\n".join(f"• {name}" for name in casetas_afectadas)
        + "\n\n📊 Revisa el detalle en el panel:\n"
        f"http://127.0.0.1:8000/"
    )
    try:
        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=settings.TWILIO_WHATSAPP_TO,
            body=resumen_msg
        )
        print(f"💬 WhatsApp enviado correctamente a {settings.TWILIO_WHATSAPP_TO}")
    except Exception as e:
        print(f"⚠️ Error al enviar WhatsApp: {e}")

        
# RESUMEN MENSUAL AUTOMÁTICO
def send_monthly_summary_pdf_email():
    """Genera y envía el resumen mensual con PDFs adjuntos (usando ReportLab actualizado)."""

    today = date.today()
    first_day, last_day = get_month_date_range(today)

    # Si no es el último día hábil, salir
    if not get_last_business_day(today):
        print("📅 Hoy no es el último día hábil del mes. No se envía resumen.")
        return

    # =====================================================
    # 1️⃣ CONSULTAS BASE
    # =====================================================
    aplicaciones = ApplicationDetail.objects.select_related(
        "application__ware", "application__applied_by", "product"
    ).filter(application__applied_at__date__range=[first_day, last_day])

    movimientos = Movement.objects.select_related(
        "product", "presentation", "ware_origin", "ware_destin", "moved_by"
    ).filter(moved_at__date__range=[first_day, last_day])

    inventario = Inventory.objects.select_related(
        "product", "presentation", "warehouse"
    ).order_by("warehouse__name_ware", "product__name_prod")

    # =====================================================
    # 2️⃣ FORMATEAR DATOS PARA PDF
    # =====================================================

    # --- Aplicaciones ---
    data_aplicaciones = [
        {
            "ID": d.application.id,
            "Fecha": d.application.applied_at.strftime("%d/%m/%Y"),
            "Caseta": d.application.ware.name_ware,
            "Producto": d.product.name_prod,
            "Cantidad paquetes": d.quantity_packages,
            "Usuario": d.application.applied_by.nombre_usuario,
        }
        for d in aplicaciones
    ]

    # --- Movimientos ---
    data_movimientos = [
        {
            "ID": m.id,
            "Fecha": m.moved_at.strftime("%d/%m/%Y"),
            "Producto": m.product.name_prod,
            "Presentación": f"{m.presentation.package_type} {m.presentation.content_value} {m.presentation.content_unit}",
            "Cantidad": m.quantity,
            "Tipo": m.movement_type.capitalize(),
            "Origen": m.ware_origin.name_ware if m.ware_origin else "—",
            "Destino": m.ware_destin.name_ware,
            "Usuario": m.moved_by.nombre_usuario if m.moved_by else "—",
            "Descripción": m.description or "",
        }
        for m in movimientos
    ]

    # --- Inventario ---
    data_inventario = [
        {
            "Bodega": i.warehouse.name_ware,
            "Producto": i.product.name_prod,
            "Presentación": f"{i.presentation.package_type} {i.presentation.content_value} {i.presentation.content_unit}",
            "Cantidad paquetes": i.quantity_packages,
            "Total contenido": i.total_content,
            "Última actualización": i.updated_at.strftime("%d/%m/%Y %H:%M"),
        }
        for i in inventario
    ]

    # =====================================================
    # 3️⃣ GENERAR PDFs USANDO REPORTLAB
    # =====================================================
    pdf_aplicaciones = BytesIO(generar_pdf_reportlab("aplicaciones", data_aplicaciones, first_day, last_day))
    pdf_movimientos = BytesIO(generar_pdf_reportlab("movimientos", data_movimientos, first_day, last_day))
    pdf_inventario = BytesIO(generar_pdf_reportlab("inventario", data_inventario, first_day, last_day))

    # =====================================================
    # RESUMEN GENERAL PARA EL CORREO
    # =====================================================
    resumen = {
        "total_aplicaciones": aplicaciones.count(),
        "total_paquetes": round(aplicaciones.aggregate(total=Sum("quantity_packages"))["total"] or 0, 2),
        "total_movimientos": movimientos.count(),
        "stock_total": round(inventario.aggregate(total=Sum("quantity_packages"))["total"] or 0, 2),
        "mes": today.strftime("%B %Y").capitalize(),
        "periodo": f"{first_day.strftime('%d/%m/%Y')} - {last_day.strftime('%d/%m/%Y')}",
    }

    # =====================================================
    # 5️⃣ ENVÍO DE CORREOS A ADMINISTRADORES
    # =====================================================
    subject = f"Resumen Mensual - Gestión Quilhuica ({resumen['mes']})"
    html_content = render_to_string("notification/monthly_summary.html", resumen)
    text_content = strip_tags(html_content)

    admins = Usuario.objects.filter(roles__name_role="Administrador", correo__isnull=False).distinct()

    if not admins.exists():
        print("⚠️ No hay administradores para enviar el resumen mensual.")
        return

    for admin in admins:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=EMAIL_FROM,
            to=[admin.correo],
        )
        email.attach_alternative(html_content, "text/html")

        email.attach(
            f"Resumen_Aplicaciones_{today.strftime('%Y_%m')}.pdf",
            pdf_aplicaciones.getvalue(),
            "application/pdf",
        )
        email.attach(
            f"Resumen_Movimientos_{today.strftime('%Y_%m')}.pdf",
            pdf_movimientos.getvalue(),
            "application/pdf",
        )
        email.attach(
            f"Resumen_Inventario_{today.strftime('%Y_%m')}.pdf",
            pdf_inventario.getvalue(),
            "application/pdf",
        )

        email.send()
        print(f"📤 Resumen mensual enviado a {admin.correo}")

    print("✅ Resumen mensual PDF enviado correctamente a todos los administradores.")

def send_monthly_summary_pdf_email_debug():
    """
    Mismo que el original, pero sin validar día hábil.
    Útil para pruebas.
    """
    from notification.utils import send_monthly_summary_pdf_email

    print("🧪 Ejecutando versión DEBUG del resumen mensual (sin restricciones)...")
    send_monthly_summary_pdf_email.__globals__['get_last_business_day'] = lambda *_: True
    send_monthly_summary_pdf_email()

def send_low_stock_alert_debug(threshold=100):
    """
    Versión DEBUG de la alerta de stock bajo.
    Omite validaciones y ejecuta el envío directamente
    para propósitos de prueba en consola o entorno local.
    """
    from notification.utils import send_low_stock_alert

    print("🧪 Ejecutando versión DEBUG de alerta de stock bajo...")
    send_low_stock_alert(threshold=threshold)