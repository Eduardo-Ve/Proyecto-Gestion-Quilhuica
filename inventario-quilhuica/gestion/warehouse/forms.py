from django import forms
from .models import Warehouse

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