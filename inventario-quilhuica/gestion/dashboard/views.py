# dashboard/views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import TruncDate
from datetime import timedelta, date

from product.models import Product
from warehouse.models import Warehouse, Inventory, Movement
import json

def index(request):
    LOW_STOCK_THRESHOLD = 5
    MOVEMENTS_DAYS = 30

    # 🔹 Filtro por caseta (warehouse)
    selected_warehouse_id = request.GET.get('warehouse', None)
    warehouses = Warehouse.objects.all().order_by('name_ware')

    # Estadísticas generales
    total_products = Product.objects.count()
    total_warehouses = warehouses.count()
    total_stock_packages = Inventory.objects.aggregate(total=Sum('quantity_packages'))['total'] or 0.0
    total_stock_units = Inventory.objects.aggregate(
        total_units=Sum(
            ExpressionWrapper(
                F('quantity_packages') * F('presentation__content_value'),
                output_field=FloatField()
            )
        )
    )['total_units'] or 0.0

    # 🔹 Stock por caseta
    stock_by_warehouse_qs = (
        Inventory.objects
        .select_related('warehouse', 'presentation')
        .values('warehouse__id', 'warehouse__name_ware', 'warehouse__type')
        .annotate(
            total_packages=Sum('quantity_packages'),
            total_units=Sum(
                ExpressionWrapper(
                    F('quantity_packages') * F('presentation__content_value'),
                    output_field=FloatField()
                )
            )
        )
        .order_by('-total_packages')
    )

    warehouse_names = []
    warehouse_packages = []
    for row in stock_by_warehouse_qs:
        if row['warehouse__type'] == 'shed':
            warehouse_names.append(row['warehouse__name_ware'])
            warehouse_packages.append(row['total_packages'] or 0)

    # 🔹 Movimientos recientes (con filtro + paginación)
    movements_qs = (
        Movement.objects
        .select_related('product', 'presentation', 'ware_origin', 'ware_destin', 'moved_by')
        .order_by('-moved_at')
    )

    if selected_warehouse_id:
        movements_qs = movements_qs.filter(ware_destin_id=selected_warehouse_id)

    paginator = Paginator(movements_qs, 10)  # 10 movimientos por página
    page_number = request.GET.get('page')
    recent_movements = paginator.get_page(page_number)

    # 🔹 Alertas de stock bajo (solo casetas)
    low_stock_qs = (
        Inventory.objects
        .select_related('product', 'presentation', 'warehouse')
        .filter(quantity_packages__lte=LOW_STOCK_THRESHOLD, warehouse__type='shed')
        .order_by('quantity_packages')[:50]
    )

    # 🔹 Movimientos por día (últimos 30 días)
    since_date = date.today() - timedelta(days=MOVEMENTS_DAYS)
    movements_over_time_qs = (
        Movement.objects
        .filter(moved_at__date__gte=since_date)
        .annotate(day=TruncDate('moved_at'))
        .values('day')
        .annotate(total_qty=Sum('quantity'))
        .order_by('day')
    )
    mov_dates = [r['day'].isoformat() for r in movements_over_time_qs]
    mov_totals = [r['total_qty'] for r in movements_over_time_qs]

    context = {
        # Datos base
        'total_products': total_products,
        'total_warehouses': total_warehouses,
        'total_stock_packages': total_stock_packages,
        'total_stock_units': total_stock_units,
        # Gráficos
        'warehouse_names': warehouse_names,
        'warehouse_packages': warehouse_packages,
        # Tablas
        'recent_movements': recent_movements,
        'low_stock_list': low_stock_qs,
        # Parámetros
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
        'mov_dates': mov_dates,
        'mov_totals': mov_totals,
        'warehouses': warehouses,
        'selected_warehouse_id': int(selected_warehouse_id) if selected_warehouse_id else None,
    }
    return render(request, 'dashboard/index.html', context)