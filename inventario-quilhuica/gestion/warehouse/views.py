# warehouse/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required

from login.decorators import role_required
from .models import Warehouse, Inventory, Movement
from .forms import WarehouseForm, TransferForm, TransferDetailFormSet
from product.models import Product  # usado en transfer_product


# =========================
# LISTADOS DE CASETAS
# =========================
def caseta_list(request):
    """
    Lista solo casetas (type='shed').
    """
    casetas = Warehouse.objects.filter(type='shed').order_by('name_ware')
    return render(request, 'warehouse/caseta_list.html', {'casetas': casetas})


# =========================
# PRODUCTOS POR CASETA (con filtro)
# =========================
def productos_por_caseta(request):
    """
    Vista principal para ver productos por caseta.
    - Si viene ?caseta=<id> se filtra y se renderiza listado plano.
    - Si NO hay filtro, se agrupa por caseta (regroup en el template).
    Importante: ordenamos por warehouse__name_ware para que regroup no repita grupos.
    """
    casetas = Warehouse.objects.filter(type='shed').order_by('name_ware')

    caseta_id = request.GET.get('caseta')  # puede venir None/'' si no hay filtro
    qs = (
        Inventory.objects
        .select_related('product', 'presentation', 'warehouse')
        .filter(warehouse__type='shed')
    )

    if caseta_id:
        inventarios = qs.filter(warehouse_id=caseta_id).order_by(
            'product__name_prod',
            'presentation__content_unit',
            'presentation__content_value',
        )
    else:
        inventarios = qs.order_by(
            'warehouse__name_ware',               # clave para que regroup funcione
            'product__name_prod',
            'presentation__content_unit',
            'presentation__content_value',
        )

    context = {
        'casetas': casetas,
        'inventarios': inventarios,
        'caseta_seleccionada': caseta_id or "",
    }
    return render(request, 'warehouse/productos_por_caseta.html', context)


# =========================
# CRUD CASETAS
# =========================
@role_required(allowed_roles=['Administrador'])
def caseta_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Caseta creada correctamente.")
            return redirect('warehouse:caseta_list')
    else:
        form = WarehouseForm()
    return render(
        request,
        'warehouse/caseta_form.html',
        {'form': form, 'title': 'Crear Caseta'}
    )


@role_required(allowed_roles=['Administrador'])
def caseta_edit(request, pk):
    caseta = get_object_or_404(Warehouse, pk=pk, type='shed')
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=caseta)
        if form.is_valid():
            form.save()
            messages.success(request, "Caseta actualizada correctamente.")
            return redirect('warehouse:caseta_list')
    else:
        form = WarehouseForm(instance=caseta)
    return render(
        request,
        'warehouse/caseta_form.html',
        {'form': form, 'title': 'Editar Caseta'}
    )


@role_required(allowed_roles=['Administrador'])
def caseta_delete(request, pk):
    caseta = get_object_or_404(Warehouse, pk=pk, type='shed')
    if request.method == "POST":
        caseta.delete()
        messages.success(request, "Caseta eliminada correctamente.")
        return redirect('warehouse:caseta_list')
    return render(request, 'warehouse/caseta_confirm_delete.html', {'caseta': caseta})


# =========================
# TRASLADO DESDE BODEGA PRINCIPAL A CASETA
# =========================
@role_required(allowed_roles=['Administrador'])
def transfer_product(request):
    try:
        ware_origin = Warehouse.objects.get(type='main')
    except Warehouse.DoesNotExist:
        messages.error(request, "Error crítico: No existe una bodega principal configurada.")
        return redirect('warehouse:caseta_list')

    # Productos con stock en bodega principal (para hints / dropdowns)
    products_in_stock = Product.objects.filter(
        inventory__warehouse=ware_origin,
        inventory__quantity_packages__gt=0
    ).distinct()

    if request.method == 'POST':
        master_form = TransferForm(request.POST)
        formset = TransferDetailFormSet(request.POST)

        if master_form.is_valid() and formset.is_valid():
            ware_destin = master_form.cleaned_data['ware_destin']
            description = master_form.cleaned_data['description']

            try:
                with transaction.atomic():
                    for form_data in formset.cleaned_data:
                        if not form_data or form_data.get('DELETE'):
                            continue

                        product = form_data['product']
                        quantity_to_move = form_data['quantity']

                        # 1) Validar stock en origen
                        inv_origin = Inventory.objects.get(product=product, warehouse=ware_origin)
                        if inv_origin.quantity_packages < quantity_to_move:
                            raise ValueError(
                                f"Stock insuficiente para {product.name_prod}. "
                                f"Disponible: {inv_origin.quantity_packages}."
                            )

                        # 2) Descontar en origen
                        inv_origin.quantity_packages -= quantity_to_move
                        inv_origin.save()

                        # 3) Aumentar en destino (respetando presentación del producto)
                        inv_dest, _ = Inventory.objects.get_or_create(
                            product=product,
                            presentation=product.presentation,
                            warehouse=ware_destin,
                            defaults={'quantity_packages': 0}
                        )
                        inv_dest.quantity_packages += quantity_to_move
                        inv_dest.save()

                        # 4) Registrar movimiento
                        Movement.objects.create(
                            product=product,
                            presentation=product.presentation,
                            ware_origin=ware_origin,
                            ware_destin=ware_destin,
                            movement_type='traslado',
                            quantity=quantity_to_move,
                            moved_by=request.user,
                            description=description
                        )

                messages.success(
                    request,
                    f"Traslado completado exitosamente a la caseta {ware_destin.name_ware}."
                )
                return redirect('warehouse:transfer_product')

            except Inventory.DoesNotExist:
                messages.error(
                    request,
                    "Error: Uno de los productos no tiene inventario en la bodega principal."
                )
            except ValueError as e:
                messages.error(request, str(e))
    else:
        master_form = TransferForm()
        formset = TransferDetailFormSet()

    context = {
        'master_form': master_form,
        'formset': formset,
        'products_in_stock': products_in_stock,
        'title': 'Trasladar Productos a Caseta',
    }
    return render(request, 'warehouse/transfer_product.html', context)


# =========================
# API: Productos por bodega (JSON)
# =========================
def get_products_by_warehouse(request, warehouse_id):
    try:
        inventory = (
            Inventory.objects
            .filter(warehouse_id=warehouse_id, quantity_packages__gt=0)
            .select_related('product', 'presentation')
        )

        data = [
            {
                "id": inv.product.product_id,
                "name": inv.product.name_prod,
                "presentation": f"{inv.presentation.content_value} {inv.presentation.content_unit}",
                "quantity": inv.quantity_packages,
            }
            for inv in inventory
        ]
        return JsonResponse(data, safe=False)

    except Exception as e:
        # Log básico a consola
        print(f"[ERROR get_products_by_warehouse] {e}")
        return JsonResponse({"error": str(e)}, status=500)
