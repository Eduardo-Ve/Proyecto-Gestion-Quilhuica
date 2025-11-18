from django import forms
from .models import Product, Presentation, Category
from warehouse.models import Warehouse, Inventory, Movement
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit

class ProductForm(forms.ModelForm):
    """
    Formulario para crear y editar productos, permitiendo:
    - Crear nuevas categorías
    - Crear nuevas presentaciones
    - Registrar stock inicial en bodega principal
    - Registrar movimientos por ajuste al editar un producto
    """
    
    create_new_category = forms.BooleanField(required=False, label="Crear nueva categoría")
    new_category_name = forms.CharField(required=False, label="Nombre de nueva categoría")
    new_category_description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': 2}), label="Descripción de categoría"
    )

    create_new_presentation = forms.BooleanField(required=False, label="Crear nueva presentación")
    package_type = forms.ChoiceField(required=False, choices=Presentation.PACKAGE_CHOICES, label="Tipo de empaque")
    content_value = forms.IntegerField(required=False, label="Contenido")
    content_unit = forms.ChoiceField(required=False, choices=Presentation.UNIT_CHOICES, label="Unidad")
    stock_inicial = forms.IntegerField(required=False, min_value=0, label="Stock Inicial")

    class Meta:
        model = Product
        fields = ['name_prod', 'category', 'presentation', 'expire_at', 'stock_inicial']
        labels = {
            'name_prod': 'Nombre del producto',
            'category': 'Categoría',
            'presentation': 'Presentación',
            'expire_at': 'Fecha de vencimiento',
            'stock_inicial': 'Stock inicial',
        }
        widgets = {
            'expire_at': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            main_warehouse = Warehouse.objects.filter(type='main').first()
            if main_warehouse:
                inv = Inventory.objects.filter(
                    product=self.instance,
                    presentation=self.instance.presentation,
                    warehouse=main_warehouse
                ).first()
                if inv:
                    self.fields['stock_inicial'].initial = inv.quantity_packages

        self.fields['category'].required = False
        self.fields['presentation'].required = False
        self.fields['category'].empty_label = "Seleccione una categoría existente"
        self.fields['presentation'].empty_label = "Seleccione una presentación existente"

    def save(self, commit=True, user=None):
        product = super().save(commit=False)

        if self.cleaned_data.get('create_new_category'):
            product.category = Category.objects.create(
                name_cat=self.cleaned_data['new_category_name'],
                description_cat=self.cleaned_data.get('new_category_description', '')
            )

        if self.cleaned_data.get('create_new_presentation'):
            product.presentation = Presentation.objects.create(
                package_type=self.cleaned_data['package_type'],
                content_value=self.cleaned_data['content_value'],
                content_unit=self.cleaned_data['content_unit']
            )

        is_new = product.pk is None

        if commit:
            product.save()
            self.save_m2m()

            stock_nuevo = self.cleaned_data.get('stock_inicial')
            main_warehouse = Warehouse.objects.filter(type='main').first()

            if stock_nuevo is not None and main_warehouse:
                inventory, _ = Inventory.objects.get_or_create(
                    product=product,
                    presentation=product.presentation,
                    warehouse=main_warehouse,
                    defaults={'quantity_packages': 0}
                )

                if is_new:
                    inventory.quantity_packages = stock_nuevo
                    inventory.save()

                    if user and user.is_authenticated and stock_nuevo > 0:
                        Movement.objects.create(
                            product=product,
                            presentation=product.presentation,
                            ware_origin=None,
                            ware_destin=main_warehouse,
                            movement_type='entrada',
                            quantity=stock_nuevo,
                            moved_by=user,
                            description=f"Entrada inicial de {stock_nuevo} unidades al crear el producto."
                        )

                else:
                    stock_anterior = inventory.quantity_packages
                    diferencia = stock_nuevo - stock_anterior

                    if diferencia != 0:
                        if diferencia > 0:
                            origen = None
                            destino = main_warehouse
                            tipo = "entrada"
                        else:
                            origen = main_warehouse
                            destino = None
                            tipo = "salida"

                        if user and user.is_authenticated:
                            Movement.objects.create(
                                product=product,
                                presentation=product.presentation,
                                ware_origin=origen,
                                ware_destin=destino,
                                movement_type=tipo,
                                quantity=abs(diferencia),
                                moved_by=user,
                                description=f"Ajuste de stock al editar producto ({'+' if diferencia > 0 else '-'}{abs(diferencia)} unidades)."
                            )

                        inventory.quantity_packages = stock_nuevo
                        inventory.save()

        return product


class StockAddForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by('name_prod'),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad a añadir (en paquetes)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 100'})
    )

    def save(self, user):
        """Actualizar inventario y registrar movimiento"""
        product = self.cleaned_data['product']
        cantidad = self.cleaned_data['cantidad']

        main_warehouse = Warehouse.objects.filter(type='main').first()
        if not main_warehouse:
            raise ValueError("No existe la bodega principal.")

        # Actualizar o crear inventario
        inventory, _ = Inventory.objects.get_or_create(
            product=product,
            presentation=product.presentation,
            warehouse=main_warehouse,
            defaults={'quantity_packages': 0}
        )

        inventory.quantity_packages += cantidad
        inventory.save()

        # Registrar movimiento
        Movement.objects.create(
            product=product,
            presentation=product.presentation,
            ware_origin=None,
            ware_destin=main_warehouse,
            movement_type='entrada',
            quantity=cantidad,
            moved_by=user,
            description=f"Entrada de {product}, añadiendo {cantidad} paquetes al stock existente."
        )