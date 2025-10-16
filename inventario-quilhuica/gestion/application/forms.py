# application/forms.py

from django import forms
from .models import Application, ApplicationDetail

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['ware'] 
        labels = {
            'ware': 'Seleccione la Caseta de Aplicación'
        }
        widgets = {
            'ware': forms.Select(attrs={'class': 'form-control'})
        }

class ApplicationDetailForm(forms.ModelForm):
    class Meta:
        model = ApplicationDetail
        fields = ['product', 'presentation', 'quantity_packages']
        labels = {
            'product': 'Producto',
            'presentation': 'Presentación',
            'quantity_packages': 'Cantidad de Paquetes'
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'presentation': forms.Select(attrs={'class': 'form-control'}),
            'quantity_packages': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# Usamos inlineformset_factory para crear un conjunto de formularios para los detalles
# Esto vincula los detalles directamente con la aplicación principal.
ApplicationDetailFormSet = forms.inlineformset_factory(
    Application,                # Modelo Padre
    ApplicationDetail,          # Modelo Hijo
    form=ApplicationDetailForm, # Formulario a usar para cada detalle
    extra=1,                    # Muestra 1 formulario vacío por defecto
    can_delete=True,            # Permite eliminar líneas si es necesario
    can_delete_extra=True,
)