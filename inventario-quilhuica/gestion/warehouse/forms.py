from django import forms
from .models import Warehouse, Movement, Inventory
from product.models import Product, Presentation
from django.forms import formset_factory
from .models import Warehouse, Movement, Inventory
from product.models import Product
from django.http import JsonResponse


#FORMULARIO PARA CREAR CASETA
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name_ware', 'description']
        widgets = {
            'name_ware': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = 'shed'  # siempre será caseta (shed = caseta | main = bodega).
        if commit:
            instance.save()
        return instance
    
#FORMULARIO PARA REGISTRAR EL TRASLADO DE PRODUCTOS HACIA LAS CASETAS
# warehouse/forms.py


# 1. FORMULARIO MAESTRO: Para seleccionar el destino una sola vez.
class TransferForm(forms.Form):
    ware_origin = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label="Origen del Producto",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'})
    )
    ware_destin = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(type='shed'),
        label="Caseta de Destino",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'})
    )
    description = forms.CharField(
        required=False,
        label="Descripción General del Traslado",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
class TransferDetailForm(forms.ModelForm):
    # Solo necesitamos el producto y la cantidad por cada fila
    class Meta:
        model = Movement
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.01}),
        }

# 3. FORMSET: Agrupa los formularios de detalle.
TransferDetailFormSet = formset_factory(
    TransferDetailForm,
    extra=1,  # Empezar con un formulario
    can_delete=True # Permitir eliminar filas
)


def get_products_by_warehouse(request, warehouse_id):
    inventory = Inventory.objects.filter(warehouse_id=warehouse_id, total_content__gt=0)
    data = [
        {"id": inv.product.id, "name": inv.product.name_prod, "presentation": inv.product.presentation.name}
        for inv in inventory
    ]
    return JsonResponse(data, safe=False)