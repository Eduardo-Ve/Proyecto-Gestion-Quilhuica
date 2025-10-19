from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Warehouse, Inventory, Movement
from .forms import *
from django.db import transaction
from django.contrib.auth.decorators import login_required
from login.decorators import role_required
# LISTAR SOLO CASETAS
def caseta_list(request):
    casetas = Warehouse.objects.filter(type='shed')
    return render(request, 'warehouse/caseta_list.html', {'casetas': casetas})

def inventory_list(request):
    casetas = Warehouse.objects.filter(type='shed')
    inventarios = Inventory.objects.filter(warehouse__in=casetas).select_related('product', 'presentation', 'warehouse')

    context = {
        'casetas': casetas,
        'inventarios': inventarios
    }
    return render(request, 'warehouse/productos_por_caseta.html', context)
# CREAR CASETA

@role_required(allowed_roles=['Administrador'])
def caseta_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warehouse:caseta_list')  
    else:
        form = WarehouseForm()
    return render(request, 'warehouse/caseta_form.html', {'form': form, 'title': 'Crear Caseta'})


# EDITAR CASETA
@role_required(allowed_roles=['Administrador'])
def caseta_edit(request, pk):
    caseta = get_object_or_404(Warehouse, pk=pk, type='shed')
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=caseta)
        if form.is_valid():
            form.save()
            return redirect('warehouse:caseta_list') 
    else:
        form = WarehouseForm(instance=caseta)
    return render(request, 'warehouse/caseta_form.html', {'form': form, 'title': 'Editar Caseta'})


# ELIMINAR CASETA
@role_required(allowed_roles=['Administrador'])
def caseta_delete(request, pk):
    caseta = get_object_or_404(Warehouse, pk=pk, type='shed')
    if request.method == "POST":
        caseta.delete()
        return redirect('warehouse:caseta_list')  
    return render(request, 'warehouse/caseta_confirm_delete.html', {'caseta': caseta})


# TRANSFERIR PRODUCTO A UNA CASETA
@role_required(allowed_roles=['Administrador'])
def transfer_product(request):
    try:
        ware_origin = Warehouse.objects.get(type='main')
    except Warehouse.DoesNotExist:
        messages.error(request, "Error crítico: No existe una bodega principal configurada.")
        return redirect('warehouse:caseta_list') # Redirigir a un lugar seguro

    # Productos que tienen stock en la bodega principal para popular el dropdown
    products_in_stock = Product.objects.filter(
        inventory__warehouse=ware_origin,
        inventory__quantity_packages__gt=0
    ).select_related('presentation').distinct()

    if request.method == 'POST':
        master_form = TransferForm(request.POST)
        formset = TransferDetailFormSet(request.POST)

        if master_form.is_valid() and formset.is_valid():
            ware_destin = master_form.cleaned_data['ware_destin']
            description = master_form.cleaned_data['description']
            
            try:
                with transaction.atomic(): # Transacción para asegurar la integridad de datos
                    # Bucle para procesar cada formulario en el formset
                    for form_data in formset.cleaned_data:
                        if not form_data or form_data.get('DELETE'):
                            continue # Ignorar formularios vacíos o marcados para borrar

                        product = form_data['product']
                        quantity_to_move = form_data['quantity']

                        # 1. Validar stock en origen
                        inv_origin = Inventory.objects.get(product=product, warehouse=ware_origin)
                        if inv_origin.quantity_packages < quantity_to_move:
                            raise ValueError(f"Stock insuficiente para {product.name_prod}. Disponible: {inv_origin.quantity_packages}.")

                        # 2. Actualizar inventario en origen
                        inv_origin.quantity_packages -= quantity_to_move
                        inv_origin.save()

                        # 3. Actualizar inventario en destino
                        inv_dest, _ = Inventory.objects.get_or_create(
                            product=product,
                            presentation=product.presentation, # Obtenemos la presentación del producto
                            warehouse=ware_destin,
                            defaults={'quantity_packages': 0}
                        )
                        inv_dest.quantity_packages += quantity_to_move
                        inv_dest.save()

                        # 4. Crear el registro del movimiento
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
                
                messages.success(request, f"Traslado completado exitosamente a la caseta {ware_destin.name_ware}.")
                return redirect('warehouse:transfer_product')

            except Inventory.DoesNotExist:
                messages.error(request, f"Error: Uno de los productos seleccionados no tiene registro de inventario en la bodega principal.")
            except ValueError as e:
                messages.error(request, str(e)) # Muestra el error de stock insuficiente

    else:
        master_form = TransferForm()
        formset = TransferDetailFormSet()

    context = {
        'master_form': master_form,
        'formset': formset,
        'products_in_stock': products_in_stock,
        'title': 'Trasladar Productos a Caseta'
    }
    return render(request, 'warehouse/transfer_product.html', context)
# LISTAR PRODUCTOS POR CASETA
def productos_por_caseta(request):
    # Obtenemos todas las casetas
    casetas = Warehouse.objects.all()

    # Obtenemos inventario relacionado con esas casetas
    inventarios = Inventory.objects.filter(warehouse__in=casetas).select_related('product', 'presentation', 'warehouse')

    context = {
        'casetas': casetas,
        'inventarios': inventarios
    }

    return render(request, 'warehouse/productos_por_caseta.html', context)

