from django import forms
from .models import Warehouse, Movement, Inventory
from product.models import Product, Presentation

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

from django import forms
from django.forms import formset_factory
from .models import Warehouse, Movement, Inventory
from product.models import Product

# ... (tus otros forms como WarehouseForm se mantienen igual) ...

# 1. FORMULARIO MAESTRO: Para seleccionar el destino una sola vez.
class TransferForm(forms.Form):
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
#formulario para registrar el ingreso de productos a la bodega principal

class InventoryEntryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        Warehouse.objects.filter(type='shed')
        fields = ["warehouse", "product", "presentation", "quantity_packages"]

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        #filtramos que solo use las warehouse de tipo shed
        # Guardamos o actualizamos el inventario
        existing = Inventory.objects.filter(
            product=instance.product,
            presentation=instance.presentation,
            warehouse=instance.warehouse
        ).first()

        if existing:
            existing.quantity_packages += instance.quantity_packages
            existing.save()
            inventory = existing
        else:
            inventory = instance
            if commit:
                inventory.save()

        # Crear registro de movimiento (entrada)
        if user:
            Movement.objects.create(
                product=inventory.product,
                presentation=inventory.presentation,
                ware_destin=inventory.warehouse,
                movement_type="entrada",
                quantity=instance.quantity_packages,
                moved_by=user,
                description="Ingreso inicial o actualización de stock"
            )

        return inventory
