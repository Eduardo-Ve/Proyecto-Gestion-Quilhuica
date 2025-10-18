from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Application, ApplicationDetail
from warehouse.models import Warehouse, Inventory # <-- Importamos Inventory
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
        self.fields['ware'].queryset = Warehouse.objects.filter(type='shed')



class ApplicationDetailForm(forms.ModelForm):
    class Meta:
        model = ApplicationDetail
        fields = ['product', 'quantity_packages']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity_packages': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


# --- FORMSET CON LA LÓGICA DE VALIDACIÓN ---
class BaseApplicationDetailFormSet(BaseInlineFormSet):
    """
    FormSet base que valida el stock de los productos contra la bodega seleccionada.
    """
    def clean(self):
        super().clean()

        # Obtenemos la bodega desde el formulario principal (ApplicationForm)
        # Si no es válido o no existe, no podemos continuar la validación.
        if not hasattr(self.instance, 'ware'):
            return
            
        warehouse = self.instance.ware

        for form in self.forms:
            # Nos saltamos los formularios que no tienen datos o están marcados para borrar
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue

            product = form.cleaned_data.get('product')
            quantity = form.cleaned_data.get('quantity_packages')

            if not product or not quantity:
                continue

            try:
                # Buscamos el stock del producto en la bodega correcta
                inventory = Inventory.objects.get(
                    product=product,
                    warehouse=warehouse
                )
                # Comparamos el stock
                if quantity > inventory.quantity_packages:
                    # Si no hay stock, añadimos un error específico a ese campo
                    form.add_error('quantity_packages', f"Stock insuficiente. Disponible: {inventory.quantity_packages}")
            
            except Inventory.DoesNotExist:
                # Si el producto ni siquiera existe en el inventario de esa bodega
                form.add_error('product', "Este producto no tiene stock en la bodega seleccionada.")


ApplicationDetailFormSet = inlineformset_factory(
    Application,
    ApplicationDetail,
    form=ApplicationDetailForm,
    formset=BaseApplicationDetailFormSet,  # <-- ¡EL CAMBIO CLAVE!
    extra=1,
    can_delete=True
)