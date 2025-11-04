import io
import os
from datetime import datetime, timedelta
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse
from .pdf_reportlab import generar_pdf_reportlab
from warehouse.models import Movement, Inventory, Warehouse
from application.models import ApplicationDetail
from login.models import Usuario
from django.contrib import messages


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
from datetime import datetime, timedelta

class ExportReportView(View):
    """Genera los reportes filtrados, con paginación y exportaciones."""

    def get(self, request):
        # ======== PARÁMETROS ========
        report_type = request.GET.get("report", "movimientos")
        start_param = request.GET.get("start")
        end_param = request.GET.get("end")
        export = request.GET.get("export")
        selected_user = request.GET.get("user")
        selected_warehouse = request.GET.get("warehouse")
        page_number = request.GET.get("page")

        # ======== FECHAS SEGURAS ========
        # si vienen vacías o "None", usar rango último mes
        try:
            if start_param and start_param.lower() != "none":
                start = datetime.strptime(start_param, "%Y-%m-%d")
            else:
                start = datetime.now() - timedelta(days=30)

            if end_param and end_param.lower() != "none":
                end = datetime.strptime(end_param, "%Y-%m-%d")
                end = datetime.strptime(end_param, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            else:
                end = datetime.now()
        except ValueError:
            # fallback si el formato está incorrecto
            start = datetime.now() - timedelta(days=30)
            end = datetime.now()

        # ======== DATOS BASE ========
        users = Usuario.objects.all().order_by("nombre_usuario")
        warehouses = Warehouse.objects.all().order_by("name_ware")

        # ======== QUERYSETS ========
        if report_type == "movimientos":
            queryset = Movement.objects.select_related(
                "product", "presentation", "ware_origin", "ware_destin", "moved_by"
            ).order_by("-moved_at")

            queryset = queryset.filter(moved_at__range=[start, end])
            if selected_user and selected_user != "":
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
                    "Cantidad": f"{m.quantity:.0f}",
                    "Usuario": m.moved_by.nombre_usuario if m.moved_by else "-",
                    "Fecha": m.moved_at.strftime("%d/%m/%Y %H:%M"),
                    "Descripción": m.description,
                }
                for m in queryset
            ]

        elif report_type == "aplicaciones":
            queryset = ApplicationDetail.objects.select_related(
                "application__ware",
                "application__applied_by",
                "product",
                "application__sector__equipment",
            ).order_by("-application__applied_at")

            queryset = queryset.filter(application__applied_at__range=[start, end])
            if selected_user:
                queryset = queryset.filter(application__applied_by__id_user=selected_user)
            if selected_warehouse:
                queryset = queryset.filter(application__ware__id=selected_warehouse)

            data = []
            for a in queryset:
                sector = a.application.sector
                data.append({
                    "id_aplicacion": a.application.id,
                    "fecha": a.application.applied_at.strftime("%d/%m/%Y %H:%M"),
                    "caseta": a.application.ware.name_ware,
                    "equipo": sector.equipment.equipo_num if sector else "No asignado",
                    "sector": sector.sector_num if sector else "No asignado",
                    "producto": a.product.name_prod,
                    "cantidad": f"{a.quantity_packages:.0f}",
                    "usuario": a.application.applied_by.nombre_usuario,
                })

        elif report_type == "inventario":
            queryset = Inventory.objects.select_related(
                "product", "presentation", "warehouse"
            ).order_by("warehouse__name_ware", "product__name_prod")

            if selected_warehouse:
                queryset = queryset.filter(warehouse__id=selected_warehouse)

            data = [
                {
                    "bodega": i.warehouse.name_ware,
                    "producto": i.product.name_prod,
                    "presentacion": str(i.presentation),
                    "cantidad_paquetes": f"{i.quantity_packages:.0f}",
                    "total_contenido": f"{i.total_content:.0f}",
                    "ultima_actualizacion": i.updated_at.strftime("%d/%m/%Y"),
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
            return self.export_pdf(request, data, report_type, start, end)

        # ======== PAGINADOR ========
        paginator = Paginator(data, 20)
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "data": page_obj.object_list,
            "report_type": report_type,
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "users": users,
            "warehouses": warehouses,
            "selected_user": selected_user or "",
            "selected_warehouse": selected_warehouse or "",
        }

        return render(request, "reports/export_template.html", context)

    # ======================================================
    # EXPORTADORES
    # ======================================================

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

    # ======================================================
    # NUEVO EXPORTADOR PDF (reportlab)
    # ======================================================
    def export_pdf(self, request, data, report_type, start, end):
        filename = self.build_filename(report_type, "pdf")
        pdf = generar_pdf_reportlab(report_type, data, start, end)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(pdf)
        return response
