from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Sum
from .models import Product
from .forms import ProductForm
from warehouse.models import *
class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Obtener la bodega principal
        main_warehouse = Warehouse.objects.filter(type='main').first()
        if not main_warehouse:
            return Product.objects.none()

        # Obtener todos los productos con inventario en la bodega principal
        products = Product.objects.filter(
            inventory__warehouse=main_warehouse
        ).distinct()

        # Agregar datos de inventario agregados
        inventory_data = (
            Inventory.objects.filter(warehouse=main_warehouse)
            .values('product')
            .annotate(
                total_packages=Sum('quantity_packages'),
                total_content=Sum('total_content')
            )
        )

        # Crear diccionario con los totales
        totals = {
            item['product']: {
                'packages': item['total_packages'] or 0,
                'content': item['total_content'] or 0
            }
            for item in inventory_data
        }

        # Inyectar los totales en cada producto
        for p in products:
            product_key = getattr(p, 'product_id', getattr(p, 'id', None))
            p.total_packages = totals.get(product_key, {}).get('packages', 0)
            p.total_content = totals.get(product_key, {}).get('content', 0)

        return products
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_create_form.html'  # Formulario de creación
    success_url = reverse_lazy('product:product_list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_update_form.html'  # Formulario de edición
    success_url = reverse_lazy('product:product_list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'  # Confirmación de eliminación
    success_url = reverse_lazy('product:product_list')
