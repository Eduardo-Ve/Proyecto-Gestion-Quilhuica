# forms.py

from django import forms
from .models import Product, Presentation, Category
from warehouse.models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,  Div, Submit

class ProductForm(forms.ModelForm):
    # Campos para nueva categoría
    create_new_category = forms.BooleanField(required=False, label="Crear nueva categoría")
    new_category_name = forms.CharField(required=False, label="Nombre de nueva categoría")
    new_category_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':2}), label="Descripción de categoría")

    # Campos para nueva presentación
    create_new_presentation = forms.BooleanField(required=False, label="Crear nueva presentación")
    package_type = forms.ChoiceField(required=False, choices=Presentation.PACKAGE_CHOICES, label="Tipo de empaque")
    content_value = forms.FloatField(required=False, label="Contenido")
    content_unit = forms.ChoiceField(required=False, choices=Presentation.UNIT_CHOICES, label="Unidad")

    # Campo stock inicial
    stock_inicial = forms.FloatField(required=False, min_value=0, label="Stock Inicial")

    class Meta:
        model = Product
        fields = ['name_prod', 'category', 'presentation', 'expire_at', 'stock_inicial']
        widgets = {
            'expire_at': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['presentation'].required = False
        self.fields['category'].empty_label = "Seleccione una categoría existente"
        self.fields['presentation'].empty_label = "Seleccione una presentación existente"

    def clean(self):
        cleaned_data = super().clean()
        create_new_category = cleaned_data.get('create_new_category')
        category = cleaned_data.get('category')
        new_category_name = cleaned_data.get('new_category_name')

        create_new_presentation = cleaned_data.get('create_new_presentation')
        presentation = cleaned_data.get('presentation')
        package_type = cleaned_data.get('package_type')
        content_value = cleaned_data.get('content_value')

        # Validación categoría
        if self.instance.pk:
            # Edición: solo validar si quiere crear nueva
            if create_new_category and not new_category_name:
                self.add_error('new_category_name', 'El nombre es obligatorio si crea una nueva categoría.')
        else:
            # Creación: obligatorio seleccionar o crear
            if not create_new_category and not category:
                self.add_error('category', 'Debe seleccionar una categoría o crear una nueva.')

        # Validación presentación
        if self.instance.pk:
            # Edición: solo validar si quiere crear nueva
            if create_new_presentation and (not package_type or not content_value):
                self.add_error('create_new_presentation', 'Debe completar todos los campos si crea una nueva presentación.')
        else:
            # Creación: obligatorio seleccionar o crear
            if not create_new_presentation and not presentation:
                self.add_error('presentation', 'Debe seleccionar una presentación o crear una nueva.')

        return cleaned_data

    def save(self, commit=True, user=None):
        product = super().save(commit=False)

        # Crear nueva categoría solo si se marcó
        if self.cleaned_data.get('create_new_category'):
            category = Category.objects.create(
                name_cat=self.cleaned_data['new_category_name'],
                description_cat=self.cleaned_data.get('new_category_description', '')
            )
            product.category = category

        # Crear nueva presentación solo si se marcó
        if self.cleaned_data.get('create_new_presentation'):
            presentation = Presentation.objects.create(
                package_type=self.cleaned_data['package_type'],
                content_value=self.cleaned_data['content_value'],
                content_unit=self.cleaned_data['content_unit']
            )
            product.presentation = presentation

        if commit:
            product.save()  # Obligatorio para generar pk
            self.save_m2m() # Por si hay relaciones ManyToMany

            # Aquí va la lógica de inventario
            stock_inicial = self.cleaned_data.get('stock_inicial')
            if stock_inicial is not None:
                main_warehouse = Warehouse.objects.filter(type='main').first()
                if main_warehouse:
                    inventory, created = Inventory.objects.get_or_create(
                        product=product,
                        presentation=product.presentation,
                        warehouse=main_warehouse,
                        defaults={'quantity_packages': stock_inicial}
                    )
                    if not created:
                        inventory.quantity_packages = stock_inicial
                        inventory.save()  # recalcula total_content automáticamente
        return product