import io
import os
from datetime import datetime
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa

from warehouse.models import Movement, Inventory, Warehouse
from application.models import ApplicationDetail
from login.models import Usuario


# -------------------- PÁGINA PRINCIPAL --------------------
class ReportHomeView(View):
    """Página principal con el formulario de filtros y reportes."""

    def get(self, request):
        users = Usuario.objects.all().order_by("nombre_usuario")
        warehouses = Warehouse.objects.all().order_by("name_ware")

        return render(
            request,
            "reports/export_template.html",
            {"users": users, "warehouses": warehouses},
        )


# -------------------- EXPORTADOR --------------------
class ExportReportView(View):
    """Genera los reportes filtrados, con paginación y exportaciones."""

    def get(self, request):
        # ======== PARAMETROS ========
        report_type = request.GET.get("report", "movimientos")
        start = request.GET.get("start")
        end = request.GET.get("end")
        export = request.GET.get("export")
        selected_user = request.GET.get("user")
        selected_warehouse = request.GET.get("warehouse")
        page_number = request.GET.get("page")

        # ======== DATOS BASE ========
        users = Usuario.objects.all().order_by("nombre_usuario")
        warehouses = Warehouse.objects.all().order_by("name_ware")

        # ======== QUERYSETS ========
        if report_type == "movimientos":
            queryset = Movement.objects.select_related(
                "product", "presentation", "ware_origin", "ware_destin", "moved_by"
            ).order_by("-moved_at")

            # Filtros dinámicos
            if start and end:
                queryset = queryset.filter(moved_at__range=[start, end])
            if selected_user:
                queryset = queryset.filter(moved_by__id_user=selected_user)
            if selected_warehouse:
                queryset = queryset.filter(ware_destin__id=selected_warehouse)

            data = [
                {
                    "ID": m.id,
                    "Tipo": m.get_movement_type_display(),
                    "Producto": m.product.name_prod,
                    "Presentación": str(m.presentation),
                    "Origen": m.ware_origin.name_ware if m.ware_origin else "Proveedor",
                    "Destino": m.ware_destin.name_ware,
                    "Cantidad": m.quantity,
                    "Usuario": m.moved_by.nombre_usuario if m.moved_by else "-",
                    "Fecha": m.moved_at.strftime("%d/%m/%Y %H:%M"),
                    "Descripción": m.description,
                }
                for m in queryset
            ]

        elif report_type == "aplicaciones":
            queryset = ApplicationDetail.objects.select_related(
                "application__ware", "application__applied_by", "product"
            ).order_by("-application__applied_by")

            if start and end:
                queryset = queryset.filter(application__applied_at__range=[start, end])
            if selected_user:
                queryset = queryset.filter(application__applied_by__id_user=selected_user)
            if selected_warehouse:
                queryset = queryset.filter(application__ware__id=selected_warehouse)

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

        elif report_type == "inventario":
            queryset = Inventory.objects.select_related(
                "product", "presentation", "warehouse"
            ).order_by("warehouse__name_ware", "product__name_prod")

            if selected_warehouse:
                queryset = queryset.filter(warehouse__id=selected_warehouse)

            data = [
                {
                    "Bodega": i.warehouse.name_ware,
                    "Producto": i.product.name_prod,
                    "Presentación": str(i.presentation),
                    "Cantidad (Paquetes)": i.quantity_packages,
                    "Total Contenido": i.total_content,
                    "Última Actualización": i.updated_at.strftime("%d/%m/%Y"),
                }
                for i in queryset
            ]
        else:
            data = []

        # ======== EXPORTADORES ========
        if export == "csv":
            return self.export_csv(data, report_type)
        elif export == "xlsx":
            return self.export_excel(data, report_type)
        elif export == "pdf":
            return self.export_pdf(data, report_type, start, end)

        # ======== PAGINADOR ========
        paginator = Paginator(data, 20)
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "data": page_obj.object_list,
            "report_type": report_type,
            "start": start,
            "end": end,
            "users": users,
            "warehouses": warehouses,
            "selected_user": selected_user,
            "selected_warehouse": selected_warehouse,
        }

        return render(request, "reports/export_template.html", context)

    # -------------------- EXPORTADORES --------------------

    def build_filename(self, report_type, extension):
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
        """Genera un PDF desde la plantilla HTML"""
        filename = self.build_filename(report_type, "pdf")
        template_path = "reports/pdf_template.html"

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

        template = get_template(template_path)
        html = template.render(context)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        pisa.CreatePDF(io.StringIO(html), dest=response)
        return response
