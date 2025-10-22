from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import render
from django.utils import timezone

import plotly.express as px
from plotly.offline import plot

from warehouse.models import Warehouse, Inventory, Movement
from product.models import Product
from application.models import Application
from notification.models import Notification

LOW_STOCK_THRESHOLD = 100     # Bajo este valor se definirá si el stock es bajo.
EXPIRING_DAYS = 60            # Bajo este valor se definirá la alerta de producto próximo a vencer.
WINDOW_DAYS = 30              # Cantidad de días hacia atrás para visualizar gráficos.

def _user_is_shed_manager(user):
    try:
        return user.has_role("Encargado de Caseta")
    except Exception:
        return False

def _get_accessible_warehouses(user, ware_param=None):
    if not user.is_authenticated:
        return Warehouse.objects.none(), None, None

    main = Warehouse.objects.filter(type="main").first()
    if not user.is_staff and _user_is_shed_manager(user) and user.caseta_asignada:
        return Warehouse.objects.filter(pk=user.caseta_asignada.pk), main, user.caseta_asignada
    elif user.is_staff:
        sheds = Warehouse.objects.filter(type="shed").order_by("name_ware")
        if ware_param:
            selected = sheds.filter(pk=ware_param).first()
            if selected:
                return Warehouse.objects.filter(pk=selected.pk), main, selected
        return sheds, main, None
    return Warehouse.objects.none(), main, None

@login_required
def dashboard(request):
    ware_param = request.GET.get("ware")
    sheds_qs, main_warehouse, selected_shed = _get_accessible_warehouses(request.user, ware_param)

    if not sheds_qs.exists():
        return render(request, "dashboard/dashboard.html", {
            "no_access": True,
            "is_staff": request.user.is_staff,
            "sheds": Warehouse.objects.filter(type="shed")[:0],
        })

    now = timezone.now()
    start_window = (now - timedelta(days=WINDOW_DAYS)).date()
    expiring_limit = now + timedelta(days=EXPIRING_DAYS)

    inv_qs = Inventory.objects.filter(warehouse__in=sheds_qs)

    total_skus = inv_qs.values("product_id").distinct().count()
    agg_pack = inv_qs.aggregate(total_packages=Sum("quantity_packages"), total_content=Sum("total_content"))
    total_packages = agg_pack.get("total_packages") or 0
    total_content = agg_pack.get("total_content") or 0
    low_stock_count = inv_qs.filter(quantity_packages__lte=LOW_STOCK_THRESHOLD).count()

    product_ids_in_sheds = inv_qs.values_list("product_id", flat=True).distinct()
    expiring_products = Product.objects.filter(
        product_id__in=product_ids_in_sheds,
        expire_at__lte=expiring_limit
    ).count()

    top_n = 15
    stock_by_product = (
        inv_qs.values("product__name_prod")
        .annotate(packages=Sum("quantity_packages"), content=Sum("total_content"))
        .order_by("-packages")[:top_n]
    )
    fig_stock = px.bar(
        x=[s["product__name_prod"] for s in stock_by_product],
        y=[s["packages"] or 0 for s in stock_by_product],
        labels={"x": "Producto", "y": "Paquetes"},
        title="Top productos por stock (paquetes)"
    )
    plot_stock = plot(fig_stock, output_type="div", include_plotlyjs=True)

    apps_qs = (
        Application.objects.filter(
            ware__in=sheds_qs,
            applied_at__date__gte=start_window
        )
        .values("applied_at__date")
        .annotate(total=Sum("details__quantity_packages"))
        .order_by("applied_at__date")
    )
    fig_apps = px.line(
        x=[a["applied_at__date"] for a in apps_qs],
        y=[a["total"] or 0 for a in apps_qs],
        labels={"x": "Fecha", "y": "Paquetes Aplicados"},
        title=f"Aplicaciones (últimos {WINDOW_DAYS} días)"
    )
    plot_apps = plot(fig_apps, output_type="div", include_plotlyjs=True)

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
    fig_moves = px.line(
        x=[m["moved_at__date"] for m in moves_qs],
        y=[m["total"] or 0 for m in moves_qs],
        labels={"x": "Fecha", "y": "Cantidad Trasladada"},
        title=f"Traslados a casetas (últimos {WINDOW_DAYS} días)"
    )
    plot_moves = plot(fig_moves, output_type="div", include_plotlyjs=True)

    cat_dist = (
        inv_qs.values("product__category__name_cat")
        .annotate(total=Sum("quantity_packages"))
        .order_by("-total")
    )
    fig_cat = px.pie(
        names=[c["product__category__name_cat"] or "Sin categoría" for c in cat_dist],
        values=[c["total"] or 0 for c in cat_dist],
        title="Distribución de stock por categoría"
    )
    plot_cat = plot(fig_cat, output_type="div", include_plotlyjs=True)

    notif_filter = Q()
    if not request.user.is_staff and _user_is_shed_manager(request.user):
        notif_filter &= (Q(user=request.user) | Q(warehouse__warehouse__in=sheds_qs))
    else:
        if selected_shed:
            notif_filter &= Q(warehouse__warehouse=selected_shed)

    notifications = (
        Notification.objects
        .filter(notif_filter)
        .select_related("product", "warehouse", "user")
        .order_by("-created_at")[:10]
    )

    all_sheds = Warehouse.objects.filter(type="shed").order_by("name_ware") if request.user.is_staff else None

    context = {
        "no_access": False,
        "is_staff": request.user.is_staff,
        "selected_shed": selected_shed,
        "sheds": all_sheds,

        "total_skus": total_skus,
        "total_packages": total_packages,
        "total_content": total_content,
        "low_stock_count": low_stock_count,
        "expiring_products": expiring_products,
        "LOW_STOCK_THRESHOLD": LOW_STOCK_THRESHOLD,
        "EXPIRING_DAYS": EXPIRING_DAYS,

        "plot_stock": plot_stock,
        "plot_apps": plot_apps,
        "plot_moves": plot_moves,
        "plot_cat": plot_cat,

        "notifications": notifications,
        "WINDOW_DAYS": WINDOW_DAYS,
    }
    # 👇 **ruta del template dentro de la app `dashboard`**
    return render(request, "dashboard/dashboard.html", context)