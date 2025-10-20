import io
import os
from datetime import datetime
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from warehouse.models import Movement, Inventory
from application.models import ApplicationDetail
# PDF (ReportLab)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template

# -------------------- VISTA PRINCIPAL --------------------
class ReportHomeView(View):
    """Página principal de reportes (formulario de selección)."""

    def get(self, request):
        return render(request, "reports/export_template.html")


# -------------------- EXPORTADOR --------------------
class ExportReportView(View):
    """Genera el reporte filtrado (HTML, Excel, CSV o PDF)."""

    def get(self, request):
        report_type = request.GET.get("report", "movimientos")
        start = request.GET.get("start")
        end = request.GET.get("end")
        export = request.GET.get("export")

        # --- Filtros de fecha seguros ---
        filters = {}
        if start and end:
            filters["moved_at__range"] = [start, end]

        # --- Reporte: MOVIMIENTOS ---
        if report_type == "movimientos":
            queryset = Movement.objects.select_related(
                "product", "presentation", "ware_origin", "ware_destin", "moved_by"
            )
            if start and end:
                queryset = queryset.filter(moved_at__range=[start, end])

            data = [
                {
                    "ID": m.id,
                    "Tipo": m.get_movement_type_display(),
                    "Producto": m.product.name_prod,
                    "Presentación": str(m.presentation),
                    "Origen": m.ware_origin.name_ware if m.ware_origin else "Proovedor",
                    "Destino": m.ware_destin.name_ware,
                    "Cantidad": m.quantity,
                    "Usuario": m.moved_by.nombre_usuario if m.moved_by else "-",
                    "Fecha": m.moved_at,
                    "Descripción": m.description,
                }
                for m in queryset
            ]

        # --- Reporte: APLICACIONES ---
        elif report_type == "aplicaciones":
            queryset = ApplicationDetail.objects.select_related(
                "application__ware", "application__applied_by", "product"
            )
            if start and end:
                queryset = queryset.filter(application__applied_at__range=[start, end])
                #funcion de filtrar segun tablas de Aplicacion
            #if application__applied_by = {lo que el usuario pida}

            data = [
                {
                    "ID Aplicación": a.application.id,
                    "Fecha": a.application.applied_at.strftime("%d/%m/%Y"),
                    "Caseta": a.application.ware.name_ware,
                    "Producto": a.product.name_prod,
                    "Cantidad": a.quantity_packages,
                    "Usuario": a.application.applied_by.nombre_usuario,
                }
                for a in queryset
            ]

        # --- Reporte: INVENTARIO ---
        elif report_type == "inventario":
            queryset = Inventory.objects.select_related("product", "presentation", "warehouse")
            data = [
                {
                    "Bodega": i.warehouse.name_ware,
                    "Producto": i.product.name_prod,
                    "Presentación": str(i.presentation),
                    "Cantidad (Paquetes)": i.quantity_packages,
                    "Total Contenido": i.total_content,
                    "Última actualización": i.updated_at.strftime("%d/%m/%Y"),
                }
                for i in queryset
            ]
        else:
            data = []

        # --- Exportación ---
        if export == "csv":
            return self.export_csv(data, report_type)
        elif export == "xlsx":
            return self.export_excel(data, report_type)
        elif export == "pdf":
            return self.export_pdf(data, report_type, start, end)

        # --- Vista HTML ---
        return render(
            request,
            "reports/export_template.html",
            {"data": data, "report_type": report_type, "start": start, "end": end},
        )

    # -------------------- EXPORTADORES --------------------

    def build_filename(self, report_type, extension):
        """Crea un nombre de archivo consistente: YYYY_MM_DD_report_tipo.ext"""
        fecha_actual = datetime.now().strftime("%Y_%m_%d")
        return f"{fecha_actual}_report_{report_type}.{extension}"

    def export_csv(self, data, report_type):
        df = pd.DataFrame(data)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.build_filename(report_type, "csv")}"'
        df.to_csv(response, index=False)
        return response

    def export_excel(self, data, report_type):
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=report_type.capitalize())
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{self.build_filename(report_type, "xlsx")}"'
        return response

    def export_pdf(self, data, report_type, start, end):
        fecha_actual = datetime.now().strftime("%Y_%m_%d")
        filename = f"{fecha_actual}_report_{report_type}.pdf"

        # Selecciona la plantilla según el tipo de reporte (puedes usar una única si quieres)
        template_path = "reports/pdf_template.html"

        # Contexto para la plantilla HTML
        context = {
            "report_type": report_type.capitalize(),
            "data": data,
            "start": start,
            "end": end,
            "fecha_generacion": datetime.now(),
            "empresa": "Gestión Quilhuica",
            "subempresa": "Quilhuica SPA",
            "logo_url": os.path.join(settings.BASE_DIR, "reports", "static", "img", "logo.png"),
        }

    # Renderizar HTML a string
        template = get_template(template_path)
        html = template.render(context)

    # Crear el PDF con xhtml2pdf
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        pisa.CreatePDF(io.StringIO(html), dest=response)

        return response