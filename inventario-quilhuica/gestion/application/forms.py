from django import forms
from django.forms import inlineformset_factory
from .models import Application, ApplicationDetail
from warehouse.models import Warehouse
from product.models import Product

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['ware']
        widgets = {
            'ware': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo casetas
        self.fields['ware'].queryset = Warehouse.objects.filter(type='shed')


class ApplicationDetailForm(forms.ModelForm):
    class Meta:
        model = ApplicationDetail
        fields = ['product', 'quantity_packages']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity_packages': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

ApplicationDetailFormSet = inlineformset_factory(
    Application,
    ApplicationDetail,
    form=ApplicationDetailForm,
    extra=1,
    can_delete=True
)
