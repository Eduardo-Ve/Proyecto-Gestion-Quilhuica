from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Warehouse, Inventory, Movement
from .forms import WarehouseForm, TransferForm, InventoryEntryForm


# LISTAR SOLO CASETAS
def caseta_list(request):
    casetas = Warehouse.objects.filter(type='shed')
    return render(request, 'warehouse/caseta_list.html', {'casetas': casetas})

def inventory_list(request):
    inventarios = Inventory.objects.select_related('product', 'presentation', 'warehouse').all()
    return render(request, 'warehouse/productos_por_caseta.html', {'inventarios': inventarios})

# CREAR CASETA
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
def caseta_delete(request, pk):
    caseta = get_object_or_404(Warehouse, pk=pk, type='shed')
    if request.method == "POST":
        caseta.delete()
        return redirect('warehouse:caseta_list')  
    return render(request, 'warehouse/caseta_confirm_delete.html', {'caseta': caseta})


# TRANSFERIR PRODUCTO A UNA CASETA
def transfer_product(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            product = form.cleaned_data['product']
            presentation = form.cleaned_data['presentation']
            ware_origin = form.cleaned_data['ware_origin']
            ware_destin = form.cleaned_data['ware_destin']
            quantity_packages = form.cleaned_data['quantity']

            # Obtener stock de origen
            try:
                inv_origin = Inventory.objects.get(product=product, presentation=presentation, warehouse=ware_origin)
            except Inventory.DoesNotExist:
                messages.error(request, "No existe stock de ese producto en la bodega principal.")
                return redirect('warehouse:transfer_product') 

            if inv_origin.quantity_packages < quantity_packages:
                messages.error(request, f"No hay suficiente stock disponible ({inv_origin.quantity_packages} unidades).")
                return redirect('warehouse:transfer_product') 
            # Actualizar inventario
            inv_origin.quantity_packages -= quantity_packages
            inv_origin.save()

            inv_dest, created = Inventory.objects.get_or_create(
                product=product, presentation=presentation, warehouse=ware_destin,
                defaults={'quantity_packages': 0}
            )
            inv_dest.quantity_packages += quantity_packages
            inv_dest.save()

            # Guardar movimiento
            movement.movement_type = 'traslado'
            movement.moved_by = request.user
            movement.save()

            messages.success(request, f"Traslado exitoso de {quantity_packages} unidades de {product.name_prod} a {ware_destin.name_ware}.")
            return redirect('warehouse:transfer_product')  
    else:
        form = TransferForm()

    return render(request, 'warehouse/transfer_product.html', {'form': form})

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

# agregar producto a bodega

def add_inventory_entry(request):
    if request.method == "POST":
        form = InventoryEntryForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Entrada registrada correctamente.")
            return redirect("warehouse:inventory_list")
    else:
        form = InventoryEntryForm()
    return render(request, "warehouse/add_entry.html", {"form": form})
