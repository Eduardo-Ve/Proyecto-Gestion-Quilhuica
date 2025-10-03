from django.shortcuts import render, redirect, get_object_or_404
from .models import Warehouse
from .forms import WarehouseForm

# LISTAR SOLO CASETAS
def caseta_list(request):
    casetas = Warehouse.objects.filter(type='shed')
    return render(request, 'warehouse/caseta_list.html', {'casetas': casetas})

# CREAR CASETA
def caseta_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('caseta_list')
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
            return redirect('caseta_list')
    else:
        form = WarehouseForm(instance=caseta)
    return render(request, 'warehouse/caseta_form.html', {'form': form, 'title': 'Editar Caseta'})

# ELIMINAR CASETA
def caseta_delete(request, pk):
    caseta = get_object_or_404(Warehouse, pk=pk, type='shed')
    if request.method == "POST":
        caseta.delete()
        return redirect('caseta_list')
    return render(request, 'warehouse/caseta_confirm_delete.html', {'caseta': caseta})
