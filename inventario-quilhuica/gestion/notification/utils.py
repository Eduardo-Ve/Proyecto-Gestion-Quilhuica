from decouple import config
from twilio.rest import Client
from warehouse.models import Inventory
from login.models import Usuario
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# --- Configuración de servicios ---
# Twilio WhatsApp
TWILIO_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = config("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = config("TWILIO_WHATSAPP_FROM")
client = Client(TWILIO_SID, TWILIO_TOKEN)

# Email
EMAIL_FROM = config("EMAIL_HOST_USER")


def send_low_stock_alert(threshold=100):
    """
    Revisa el inventario y envía alertas de bajo stock a los administradores
    por WhatsApp y correo electrónico.
    """
    # 1. Definimos los tipos de bodega a revisar
    tipos_de_bodega = ['shed', 'main']
    
    # 2. Buscamos productos con bajo stock en esas bodegas
    low_stock_items = Inventory.objects.filter(
        warehouse__type__in=tipos_de_bodega, 
        quantity_packages__lte=threshold
    )

    if not low_stock_items.exists():
        print("No se encontraron productos con bajo stock. Tarea finalizada.")
        return

    # 3. Buscamos a los administradores con datos de contacto válidos (forma robusta)
    print("Buscando administradores con datos de contacto...")
    admins = Usuario.objects.filter(
        roles__name_role="Administrador",  # Filtra a través de la relación
        telefono__isnull=False,
        correo__isnull=False
    ).distinct()

    if not admins.exists():
        print("Productos con bajo stock encontrados, pero no hay administradores para notificar.")
        return
    
    print(f"Se encontraron {admins.count()} administradores para notificar.")

    # 4. Construimos el mensaje de alerta
    whatsapp_msg = " Alerta de Stock Bajo:\n"
    for item in low_stock_items:
        whatsapp_msg += f"- {item.product.name_prod} | Ubicación: {item.warehouse.name_ware} | Cantidad: {item.quantity_packages}\n"

    # 5. Enviamos las alertas a cada administrador
    for admin in admins:
        # --- Envío por WhatsApp ---
        try:
            message = client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{admin.telefono}",
                body=whatsapp_msg
            )
            print(f"WhatsApp enviado a {admin.nombre_usuario}, SID: {message.sid}")
        except Exception as e:
            print(f"Error enviando WhatsApp a {admin.nombre_usuario}: {str(e)}")

        # --- Envío por Email ---
        try:
            # Preparamos el contenido del correo desde una plantilla HTML
            html_content = render_to_string('notification/low_stock_alert.html', {'low_stock_items': low_stock_items, 'admin_name': admin.nombre_usuario})
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject="Alerta de Stock Bajo",
                body=text_content,
                from_email=EMAIL_FROM,
                to=[admin.correo],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            print(f"Correo enviado a {admin.nombre_usuario} ({admin.correo})")
        except Exception as e:
            print(f"Error enviando correo a {admin.nombre_usuario}: {str(e)}")