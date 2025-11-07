from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.utils.timesince import timesince
import json

from warehouse.models import Warehouse, Inventory, Movement
from product.models import Product
from application.models import Application, ApplicationDetail
from notification.models import Notification

LOW_STOCK_THRESHOLD = 100     # Stock bajo
EXPIRING_DAYS = 60            # Productos próximos a vencer
WINDOW_DAYS = 30              # Días hacia atrás para análisis


# --- Funciones auxiliares ---
def _user_is_shed_manager(user):
    try:
        return user.has_role(["Encargado Caseta", 'Supervisor'])
    except Exception:
        return False


def _get_accessible_warehouses(user, ware_param=None):
    """Devuelve las casetas o bodegas accesibles para el usuario."""
    if not user.is_authenticated:
        return Warehouse.objects.none(), None, None

    main = Warehouse.objects.filter(type="main").first()

    #  Encargado de Caseta (no staff)
    if not user.is_staff and _user_is_shed_manager(user):
        sheds = user.ware_assig.all()

        # Si tiene parámetro de filtro (solo en vistas con GET ?ware=)
        if ware_param:
            selected = sheds.filter(pk=ware_param).first()
            if selected:
                return Warehouse.objects.filter(pk=selected.pk), main, selected

        # Si tiene una o más casetas asignadas
        if sheds.exists():
            return sheds, main, None

        # Si no tiene casetas
        return Warehouse.objects.none(), main, None

    #  Administrador o Staff
    elif user.is_staff:
        sheds = Warehouse.objects.filter(type="shed").order_by("name_ware")

        if ware_param:
            selected = sheds.filter(pk=ware_param).first()
            if selected:
                return Warehouse.objects.filter(pk=selected.pk), main, selected

        return sheds, main, None

    #  Ninguna coincidencia
    return Warehouse.objects.none(), main, None



# --- Vista principal del dashboard ---
@login_required
def dashboard(request):
    ware_param = request.GET.get("ware")
    sheds_qs, main_warehouse, selected_shed = _get_accessible_warehouses(request.user, ware_param)

    if not sheds_qs.exists():
        return render(request, "dashboard/dashboard.html", {
            "no_access": True,
            "is_staff": request.user.is_staff,
            "sheds": sheds_qs,
        })

    now = timezone.now()
    start_window = (now - timedelta(days=WINDOW_DAYS)).date()
    expiring_limit = now + timedelta(days=EXPIRING_DAYS)

    # --- 🔹 Inventario actual (solo productos activos) ---
    inv_qs = Inventory.objects.filter(
        warehouse__in=sheds_qs,
        product__is_active=True
    )

    # --- KPI data ---
    total_skus = inv_qs.values("product_id").distinct().count()
    agg_pack = inv_qs.aggregate(total_packages=Sum("quantity_packages"), total_content=Sum("total_content"))
    total_packages = agg_pack.get("total_packages") or 0
    total_content = agg_pack.get("total_content") or 0
    low_stock_count = inv_qs.filter(quantity_packages__lte=LOW_STOCK_THRESHOLD).count()

    # --- 🔹 Productos activos próximos a vencer ---
    product_ids_in_sheds = inv_qs.values_list("product_id", flat=True).distinct()
    expiring_products = Product.objects.filter(
        product_id__in=product_ids_in_sheds,
        is_active=True,              # ✅ solo activos
        expire_at__lte=expiring_limit
    ).count()

    # --- 🔹 Stock actual por producto ---
    top_n = 15
    stock_by_product = (
        inv_qs.values("product__name_prod")
        .annotate(packages=Sum("quantity_packages"), content=Sum("total_content"))
        .order_by("-packages")[:top_n]
    )

    # --- 🔸 Aplicaciones y movimientos (históricos, sin filtro de is_active) ---
    apps_qs = (
        Application.objects.filter(
            ware__in=sheds_qs,
            applied_at__date__gte=start_window
        )
        .values("applied_at__date")
        .annotate(total=Sum("details__quantity_packages"))
        .order_by("applied_at__date")
    )

    moves_qs = (
        Movement.objects.filter(
            movement_type="traslado",
            ware_destin__in=sheds_qs,
            moved_at__date__gte=start_window
        )
        .values("moved_at__date")
        .annotate(total=Sum("quantity"))
        .order_by("moved_at__date")
    )

    # --- 🔸 Productos más usados (histórico, sin filtrar activos) ---
    top_used = (
        ApplicationDetail.objects.filter(
            application__ware__in=sheds_qs,
            application__applied_at__date__gte=start_window
        )
        .values("product__name_prod")
        .annotate(total_used=Sum("quantity_packages"))
    )

    # --- Serialización Chart.js ---
    chart_data = {
        "stock_labels": [s["product__name_prod"] for s in stock_by_product],
        "stock_values": [s["packages"] or 0 for s in stock_by_product],
        "apps_labels": [a["applied_at__date"].strftime("%Y-%m-%d") for a in apps_qs],
        "apps_values": [a["total"] or 0 for a in apps_qs],
        "moves_labels": [m["moved_at__date"].strftime("%Y-%m-%d") for m in moves_qs],
        "moves_values": [m["total"] or 0 for m in moves_qs],
        "used_labels": [u["product__name_prod"] for u in top_used],
        "used_values": [u["total_used"] for u in top_used],
    }

    chart_json = json.dumps(chart_data)

    # --- Notificaciones ---
    notif_filter = Q()
    if not request.user.is_staff and _user_is_shed_manager(request.user):
        notif_filter &= (Q(user=request.user) | Q(warehouse__warehouse__in=sheds_qs))
    elif selected_shed:
        notif_filter &= Q(warehouse__warehouse=selected_shed)

    notifications = (
        Notification.objects
        .filter(notif_filter)
        .select_related("product", "warehouse", "user")
        .order_by("-created_at")[:10]
    )

    # --- Actividad reciente (sin filtro de activos, para mantener trazabilidad) ---
    recent_movements = Movement.objects.select_related("product", "ware_destin", "moved_by").order_by("-moved_at")[:10]
    recent_applications = Application.objects.select_related("ware", "applied_by").order_by("-applied_at")[:10]

    recent_activity = []
    for m in recent_movements:
        recent_activity.append({
            "type": "movement",
            "timestamp": m.moved_at,
            "user": m.moved_by.nombre_usuario if m.moved_by else "—",
            "message": (
                f"Traslado de {m.quantity} {m.product.name_prod} a {m.ware_destin.name_ware}"
                if m.movement_type == "traslado"
                else f"Ingreso de {m.product.name_prod} al inventario principal"
            ),
        })

    for a in recent_applications:
        recent_activity.append({
            "type": "application",
            "timestamp": a.applied_at,
            "user": a.applied_by.nombre_usuario if a.applied_by else "—",
            "message": f"Aplicación realizada en {a.ware.name_ware}",
        })

    recent_activity = sorted(recent_activity, key=lambda x: x["timestamp"], reverse=True)[:10]

    context = {
        "no_access": False,
        "is_staff": request.user.is_staff,
        "selected_shed": selected_shed,
        "sheds": Warehouse.objects.filter(type="shed"),
        "total_skus": total_skus,
        "total_packages": total_packages,
        "total_content": total_content,
        "low_stock_count": low_stock_count,
        "expiring_products": expiring_products,
        "LOW_STOCK_THRESHOLD": LOW_STOCK_THRESHOLD,
        "EXPIRING_DAYS": EXPIRING_DAYS,
        "WINDOW_DAYS": WINDOW_DAYS,
        "chart_json": chart_json,
        "notifications": notifications,
        "recent_activity": recent_activity,
    }

    return render(request, "dashboard/dashboard.html", context)


# SECCIÓN AJAX PARA "ACTIVIDAD RECIENTE".
def activity_feed_api(request):
    """
    Devuelve {items: [...]} con la actividad reciente (máx. 20).
    Usa el mismo criterio que en el dashboard.
    """
    now = timezone.now()
    start_window = now - timedelta(days=WINDOW_DAYS)

    # 1) Movimientos a casetas
    moves = (
        Movement.objects.filter(
            movement_type="traslado",
            moved_at__gte=start_window
        )
        .select_related("product", "ware_destin", "moved_by")
        .order_by("-moved_at")[:20]
    )

    # 2) Aplicaciones
    apps = (
        Application.objects.filter(applied_at__gte=start_window)
        .select_related("ware", "applied_by")
        .order_by("-applied_at")[:20]
    )

    items = []

    for m in moves:
        items.append({
            "kind": "move",
            "title": f"Traslado de {m.quantity:g} {m.product.name_prod} a {m.ware_destin.name_ware}",
            "by": m.moved_by.nombre_usuario if m.moved_by else "—",
            "ts": m.moved_at.isoformat(),
            "when": timesince(m.moved_at, now) + " atrás",
            "icon": "arrow-left-right",  # bootstrap icon
        })

    for a in apps:
        qty = a.details.aggregate(total=Sum("quantity_packages"))["total"] or 0
        items.append({
            "kind": "app",
            "title": f"Aplicación realizada en {a.ware.name_ware}",
            "subtitle": f"Paquetes aplicados: {qty:g}",
            "by": a.applied_by.nombre_usuario if a.applied_by else "—",
            "ts": a.applied_at.isoformat(),
            "when": timesince(a.applied_at, now) + " atrás",
            "icon": "droplet",  # bootstrap icon
        })

    # mezcla y limita
    items.sort(key=lambda x: x["ts"], reverse=True)
    items = items[:20]

    resp = JsonResponse({"items": items})
    # Evita caches intermedias
    resp["Cache-Control"] = "no-store"
    return resp


ERROR_MESSAGES = {
    400: "Parece que algo salió mal con la información. Revisa los datos o recarga la pagina",
    403: "No tienes permisos para acceder a esta sección.",
    404: "La página que buscas no existe o fue movida. Verifica la dirección o regresa al inicio.",
    500: "Ocurrió un problema inesperado en el sistema. Estamos trabajando para solucionarlo, por favor inténtalo más tarde."
}

def error_400(request, exception=None):
    return render(request, "errors/error.html", {"code": 400, "message": ERROR_MESSAGES[400]}, status=400)

def error_403(request, exception=None):
    return render(request, "errors/error.html", {"code": 403, "message": ERROR_MESSAGES[403]}, status=403)

def error_404(request, exception=None):
    return render(request, "errors/error.html", {"code": 404, "message": ERROR_MESSAGES[404]}, status=404)

def error_500(request):
    return render(request, "errors/error.html", {"code": 500, "message": ERROR_MESSAGES[500]}, status=500)


# la funcion para tomar los productos serian 
# quien(get.user) cuando(filter by date ) donde (warehouse.models inventory && Warehouse) name_warehouse,  que se aplico (get prodcuts filter applyd)

def test_error_page(request):
    return render(request, "errors/error.html", {"code": 404, "message": ERROR_MESSAGES[404] })