from django import forms
from .models import Warehouse, Movement
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
