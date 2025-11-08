from django import forms
from django.forms import modelformset_factory, formset_factory
from django.http import JsonResponse
from .models import Warehouse, Equipment, Sector, Movement, Inventory
from product.models import Product

#  FORMULARIO PRINCIPAL DE CASETAS
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name_ware', 'description']
        widgets = {
            'name_ware': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name_ware': 'Nombre de la caseta',
            'description': 'Descripción',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = 'shed'
        if commit:
            instance.save()
        return instance




#  FORMULARIO DE EQUIPOS (campo virtual sectores_count)

class EquipmentForm(forms.ModelForm):
    sectores_count = forms.IntegerField(
        label="Sectores por equipo",
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
    )

    class Meta:
        model = Equipment
        fields = ['nombre_equipo']  # Cambiado desde equipo_num
        widgets = {
            'nombre_equipo': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'nombre_equipo': 'Nombre del equipo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['sectores_count'].initial = self.instance.sectores.count()


#  FORMSET DE EQUIPOS

EquipmentFormSet = modelformset_factory(
    Equipment,
    form=EquipmentForm,
    extra=0,
    can_delete=True
)
#  FORMULARIO DE TRASLADO (MAESTRO)

class TransferForm(forms.Form):
    ware_origin = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label="Origen del producto",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'}),
    )
    ware_destin = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(type='shed'),
        label="Caseta de destino",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg mb-3'}),
    )
    description = forms.CharField(
        required=False,
        label="Descripción general del traslado",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )



#  FORMULARIO DE DETALLE DE TRASLADO

class TransferDetailForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.01}),
        }
        labels = {
            'product': 'Producto',
            'quantity': 'Cantidad a trasladar',
        }
TransferDetailFormSet = formset_factory(
    TransferDetailForm,
    extra=1,      # cantidad inicial de filas
    can_delete=True  # permite eliminar filas
)


#  API: Productos por bodega (AJAX)

def get_products_by_warehouse(request, warehouse_id):
    """Devuelve productos disponibles por bodega (para AJAX)."""
    inventory = Inventory.objects.filter(warehouse_id=warehouse_id, total_content__gt=0)
    data = [
        {
            "id": inv.product.id,
            "name": inv.product.name_prod,
            "presentation": inv.product.presentation.name,
        }
        for inv in inventory
    ]
    return JsonResponse(data, safe=False)
