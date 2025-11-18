import io
import pandas as pd
from datetime import datetime, timedelta
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.contrib import messages

from warehouse.models import Movement, Inventory, Warehouse
from application.models import ApplicationDetail
from login.models import Usuario
from .pdf_reportlab import generar_pdf_reportlab

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ReportarProblemaForm
from .models import ProblemReport

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

# ============================================================
#  PÁGINA PRINCIPAL DE REPORTES
# ============================================================
class ReportHomeView(View):
    def get(self, request):
        user = request.user
        users = Usuario.objects.all().order_by("nombre_usuario")

        #  Filtro de bodegas visible según rol
        if user.is_authenticated:
            if user.is_admin:
                warehouses = Warehouse.objects.all().order_by("name_ware")
            elif user.has_role("Supervisor"):
                warehouses = Warehouse.objects.filter(
                    models.Q(id__in=user.ware_assig.all()) |
                    models.Q(name_ware__icontains="Bodega Principal")
                ).order_by("name_ware")
            elif user.ware_assig.exists():
                warehouses = user.ware_assig.all().order_by("name_ware")
            else:
                warehouses = Warehouse.objects.none()
        else:
            warehouses = Warehouse.objects.none()

        return render(
            request,
            "reports/export_template.html",
            {"users": users, "warehouses": warehouses},
        )


# ============================================================
#  EXPORTADOR DE REPORTES
# ============================================================
class ExportReportView(View):
    """Genera los reportes filtrados, con paginación y exportaciones."""

    def get(self, request):
        # ---------------- PARÁMETROS ----------------
        report_type = request.GET.get("report", "movimientos")
        start_param = request.GET.get("start")
        end_param = request.GET.get("end")
        export = request.GET.get("export")
        selected_user = request.GET.get("user")
        selected_warehouse = request.GET.get("warehouse")
        page_number = request.GET.get("page")
        user = request.user

        # ---------------- FECHAS SEGURAS ----------------
        try:
            if start_param and start_param.lower() != "none":
                start = datetime.strptime(start_param, "%Y-%m-%d")
            else:
                start = datetime.now() - timedelta(days=30)

            if end_param and end_param.lower() != "none":
                end = datetime.strptime(end_param, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            else:
                end = datetime.now()
        except ValueError:
            start = datetime.now() - timedelta(days=30)
            end = datetime.now()

        # ---------------- FILTRO POR ROL ----------------
        if user.is_authenticated:
            if user.is_admin:
                allowed_warehouses = Warehouse.objects.all()
            elif user.has_role("Supervisor"):
                #  Supervisor ve sus casetas asignadas + Bodega Principal
                allowed_warehouses = Warehouse.objects.filter(
                    models.Q(id__in=user.ware_assig.all()) |
                    models.Q(name_ware__icontains="Bodega Principal")
                )
            elif user.ware_assig.exists():
                allowed_warehouses = user.ware_assig.all()
            else:
                allowed_warehouses = Warehouse.objects.none()
        else:
            allowed_warehouses = Warehouse.objects.none()

        #  REPORTES: MOVIMIENTOS
        if report_type == "movimientos":
            queryset = (
                Movement.objects.select_related(
                    "product", "presentation", "ware_origin", "ware_destin", "moved_by"
                )
                .filter(moved_at__range=[start, end])
                .filter(
                    models.Q(ware_destin__in=allowed_warehouses)
                    | models.Q(ware_origin__in=allowed_warehouses)
                )
                .order_by("-moved_at")
            )

            if selected_user:
                queryset = queryset.filter(moved_by__id_user=selected_user)

            if selected_warehouse:
                queryset = queryset.filter(
                    models.Q(ware_destin__id=selected_warehouse) |
                    models.Q(ware_origin__id=selected_warehouse)
                )

            data = []
            for m in queryset:
                descripcion = (m.description or "").lower()

                # =====================
                # ORIGEN
                # =====================
                if m.ware_origin:
                    origen = m.ware_origin.name_ware

                else:
                    # Entrada inicial de producto
                    if "crear el producto" in descripcion:
                        origen = "Proveedor"

                    # Ajuste positivo al editar producto
                    elif "ajuste de stock" in descripcion:
                        origen = "Ajuste Interno"

                    else:
                        origen = "Ajuste Interno"

                # =====================
                # DESTINO
                # =====================
                if m.ware_destin:
                    destino = m.ware_destin.name_ware

                else:
                    # Salida por ajuste negativo
                    if "ajuste de stock" in descripcion:
                        destino = "Ajuste / Eliminación"
                    else:
                        destino = "Ajuste / Eliminación"

                # =====================
                # ARMAR FILA
                # =====================
                data.append({
                    "ID": m.id,
                    "Tipo": m.get_movement_type_display(),
                    "Producto": m.product.name_prod,
                    "Presentación": str(m.presentation),
                    "Origen": origen,
                    "Destino": destino,
                    "Cantidad": f"{m.quantity:.0f}",
                    "Usuario": m.moved_by.nombre_usuario if m.moved_by else "-",
                    "Fecha": m.moved_at.strftime("%d/%m/%Y %H:%M"),
                    "Descripción": m.description,
                })

        #  REPORTES: INVENTARIO
        elif report_type == "inventario":
            queryset = (
                Inventory.objects.select_related("product", "presentation", "warehouse")
                .filter(warehouse__in=allowed_warehouses)
                .order_by("warehouse__name_ware", "product__name_prod")
            )

            if selected_warehouse and selected_warehouse not in ["", "None"]:
                queryset = queryset.filter(warehouse__id=int(selected_warehouse))

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

        #  REPORTES: APLICACIONES
        elif report_type == "aplicaciones":
            queryset = (
                ApplicationDetail.objects.select_related(
                    "application__ware",
                    "application__applied_by",
                    "product",
                    "application__sector__equipment",
                )
                .filter(
                    application__applied_at__range=[start, end],
                    application__ware__in=allowed_warehouses,
                )
                .order_by("-application__applied_at")
            )

            if selected_user:
                queryset = queryset.filter(application__applied_by__id_user=selected_user)
            if selected_warehouse:
                queryset = queryset.filter(application__ware__id=selected_warehouse)

            data = []
            for a in queryset:
                sector = a.application.sector
                data.append(
                    {
                        "id_aplicacion": a.application.id,
                        "fecha": a.application.applied_at.strftime("%d/%m/%Y %H:%M"),
                        "caseta": a.application.ware.name_ware,
                        "equipo": sector.equipment.nombre_equipo if sector and sector.equipment else "No asignado",
                        "sector": sector.sector_num if sector else "No asignado",
                        "producto": a.product.name_prod,
                        "cantidad": f"{a.quantity_packages:.0f}",
                        "usuario": a.application.applied_by.nombre_usuario,
                    }
                )
        else:
            data = []

        #  EXPORTADORES
        if export == "csv":
            return self.export_csv(data, report_type)
        elif export == "xlsx":
            return self.export_excel(data, report_type)
        elif export == "pdf":
            return self.export_pdf(request, data, report_type, start, end)

        #  PAGINADOR Y CONTEXTO FINAL
        paginator = Paginator(data, 20)
        page_obj = paginator.get_page(page_number)

        #  Volvemos a recalcular bodegas visibles (por rol)
        if user.is_admin:
            warehouses = Warehouse.objects.all().order_by("name_ware")
        elif user.has_role("Supervisor"):
            warehouses = Warehouse.objects.filter(
                models.Q(id__in=user.ware_assig.all()) |
                models.Q(name_ware__icontains="Bodega Principal")
            ).order_by("name_ware")
        elif user.ware_assig.exists():
            warehouses = user.ware_assig.all().order_by("name_ware")
        else:
            warehouses = Warehouse.objects.none()

        context = {
            "page_obj": page_obj,
            "data": page_obj.object_list,
            "report_type": report_type,
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "users": Usuario.objects.all().order_by("nombre_usuario"),
            "warehouses": warehouses,
            "selected_user": selected_user or "",
            "selected_warehouse": selected_warehouse or "",
        }

        return render(request, "reports/export_template.html", context)

    # ====================================================
    #  EXPORTADORES AUXILIARES
    # ====================================================
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

    def export_pdf(self, request, data, report_type, start, end):
        filename = self.build_filename(report_type, "pdf")
        pdf = generar_pdf_reportlab(report_type, data, start, end)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(pdf)
        return response



@login_required
def reportar_problema(request):
    if request.method == 'POST':
        form = ReportarProblemaForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            messages.success(request, "Tu reporte fue enviado correctamente ✅")
        return redirect('reports:reportar_problema')

    else:
        form = ReportarProblemaForm()

    return render(request, 'reports/reportar_problema.html', {'form': form})


def is_admin_user(user):
    try:
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.has_role("Administrador"):
            return True
        raise PermissionDenied
    except Exception:
        raise PermissionDenied
    
@user_passes_test(is_admin_user)
def admin_problem_panel(request):
    reports = ProblemReport.objects.select_related('user').all()
    status_filter = request.GET.get('status')
    module_filter = request.GET.get('module')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if module_filter:
        reports = reports.filter(module=module_filter)

    return render(request, 'reports/admin_problem_panel.html', {
        'reports': reports,
        'status_choices': ProblemReport.STATUS_CHOICES,
        'module_choices': ProblemReport.MODULE_CHOICES,
    })

@user_passes_test(is_admin_user)
def change_report_status(request, pk):
    report = get_object_or_404(ProblemReport, pk=pk)
    if request.method == 'POST':
        report.status = request.POST.get('status', report.status)
        report.admin_comment = request.POST.get('comment', '')
        report.save()
        messages.success(request, "El estado del reporte fue actualizado correctamente.")
    return redirect('reports:admin_problem_panel')