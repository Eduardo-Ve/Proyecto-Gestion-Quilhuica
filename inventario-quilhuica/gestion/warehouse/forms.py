from django import forms
from .models import Warehouse, Movement, Inventory
from product.models import Product, Presentation

#FORMULARIO PARA CREAR CASETA
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name_ware', 'description', 'type']
        widgets = {
            'name_ware': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = 'shed'  # siempre será caseta (shed = caseta | main = bodega).
        if commit:
            instance.save()
        return instance
    
#FORMULARIO PARA REGISTRAR EL TRASLADO DE PRODUCTOS HACIA LAS CASETAS
class TransferForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    presentation = forms.ModelChoiceField(
        queryset=Presentation.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ware_origin = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(type='main'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ware_destin = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(type='shed'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.FloatField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

    class Meta:
        model = Movement
        fields = ['product', 'presentation', 'ware_origin', 'ware_destin', 'quantity', 'description']


#formulario para registrar el ingreso de productos a la bodega principal

class InventoryEntryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["warehouse", "product", "presentation", "quantity_packages"]

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

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
