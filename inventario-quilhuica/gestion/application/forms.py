from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Application, ApplicationDetail
from warehouse.models import Warehouse, Inventory, Sector
from product.models import Product

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['ware', 'sector']
        widgets = {
            'ware': forms.Select(attrs={'class': 'form-select', 'id': 'id_ware'}),
            'sector': forms.Select(attrs={'class': 'form-select', 'id': 'id_sector'}),
        }
        labels = {
            'ware': 'Caseta',
            'sector': 'Sector (Equipo — Sector)',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Campos requeridos
        self.fields['ware'].required = True
        self.fields['sector'].required = True

        # 🔹 Filtrar casetas visibles según el tipo de usuario
        if user:
            if user.is_staff:
                # El administrador ve todas las casetas tipo "shed"
                self.fields['ware'].queryset = Warehouse.objects.filter(type='shed')
            else:
                # El encargado solo ve sus casetas asignadas
                user_casetas = user.ware_assig.all()

                if user_casetas.count() == 1:
                    # Si solo tiene una caseta → se fija y bloquea
                    caseta = user_casetas.first()
                    self.fields['ware'].queryset = Warehouse.objects.filter(id=caseta.id)
                    self.fields['ware'].initial = caseta
                    self.fields['ware'].disabled = True
                elif user_casetas.exists():
                    # Si tiene varias → se listan todas
                    self.fields['ware'].queryset = user_casetas
                else:
                    # Sin casetas asignadas → no puede aplicar
                    self.fields['ware'].queryset = Warehouse.objects.none()
                    self.fields['ware'].disabled = True

        # 🔹 Sector: vacío por defecto
        self.fields['sector'].queryset = Sector.objects.none()

        # Si viene en POST (cuando cambia la caseta)
        if 'ware' in self.data:
            try:
                ware_id = int(self.data.get('ware'))
                self.fields['sector'].queryset = (
                    Sector.objects
                    .filter(equipment__caseta_id=ware_id)
                    .select_related('equipment')
                    .order_by('equipment__nombre_equipo', 'sector_num')
                )
            except (ValueError, TypeError):
                pass

        # Si estamos editando una instancia existente
        elif self.instance and getattr(self.instance, 'ware_id', None):
            ware = self.instance.ware
            self.fields['sector'].queryset = (
                Sector.objects
                .filter(equipment__caseta=ware)
                .select_related('equipment')
                .order_by('equipment__nombre_equipo', 'sector_num')
            )

    def clean_sector(self):
        sector = self.cleaned_data.get('sector')
        ware = self.cleaned_data.get('ware')
        if sector and ware and sector.equipment.caseta_id != ware.id:
            raise forms.ValidationError("El sector seleccionado no pertenece a la caseta indicada.")
        return sector
    
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
        # Capturamos warehouse y lo sacamos de kwargs ANTES del super
        self.warehouse = kwargs.pop('warehouse', None)
        super().__init__(*args, **kwargs)

        if self.warehouse:
            product_ids = Inventory.objects.filter(
                warehouse=self.warehouse
            ).values_list('product_id', flat=True)
            for form in self.forms:
                form.fields['product'].queryset = Product.objects.filter(product_id__in=product_ids)
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
