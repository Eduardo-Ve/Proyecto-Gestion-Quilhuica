from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Application, ApplicationDetail
from warehouse.models import Warehouse, Inventory
from product.models import Product


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['ware']
        widgets = {
            'ware': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            if user.is_staff:
                self.fields['ware'].queryset = Warehouse.objects.filter(type='shed')
            else:
                if user.caseta_asignada:
                    self.fields['ware'].queryset = Warehouse.objects.filter(id=user.caseta_asignada.id)
                    self.fields['ware'].initial = user.caseta_asignada
                    self.fields['ware'].disabled = True
                else:
                    self.fields['ware'].queryset = Warehouse.objects.none()
                    self.fields['ware'].disabled = True


class ApplicationDetailForm(forms.ModelForm):
    class Meta:
        model = ApplicationDetail
        fields = ['product', 'quantity_packages']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity_packages': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'product': 'Producto',
            'quantity_packages': 'Cantidad de paquetes',
        }

    def __init__(self, *args, **kwargs):
        warehouse = kwargs.pop('warehouse', None)
        super().__init__(*args, **kwargs)
        if warehouse:
            product_ids = Inventory.objects.filter(warehouse=warehouse).values_list('product_id', flat=True)
            self.fields['product'].queryset = Product.objects.filter(product_id__in=product_ids)
        else:
            self.fields['product'].queryset = Product.objects.none()


class BaseApplicationDetailFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.warehouse = kwargs.pop('warehouse', None)
        super().__init__(*args, **kwargs)

        # ✅ Asignar queryset de productos por bodega
        if self.warehouse:
            product_ids = Inventory.objects.filter(
                warehouse=self.warehouse
            ).values_list('product_id', flat=True)

            for form in self.forms:
                form.fields['product'].queryset = Product.objects.filter(
                    product_id__in=product_ids
                )
        else:
            for form in self.forms:
                form.fields['product'].queryset = Product.objects.none()

    def clean(self):
        super().clean()
        warehouse = getattr(self.instance, 'ware', None)
        if not warehouse:
            return

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue

            product = form.cleaned_data.get('product')
            quantity = form.cleaned_data.get('quantity_packages')
            if not product or not quantity:
                continue

            try:
                inventory = Inventory.objects.get(product=product, warehouse=warehouse)
                if quantity > inventory.quantity_packages:
                    form.add_error('quantity_packages', f"Stock insuficiente. Disponible: {inventory.quantity_packages}")
            except Inventory.DoesNotExist:
                form.add_error('product', "Este producto no tiene stock en la bodega seleccionada.")


ApplicationDetailFormSet = inlineformset_factory(
    Application,
    ApplicationDetail,
    form=ApplicationDetailForm,
    formset=BaseApplicationDetailFormSet,
    extra=1,
    can_delete=True
)