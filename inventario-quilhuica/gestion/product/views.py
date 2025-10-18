from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Product
from .forms import ProductForm
from warehouse.models import * 
from django.db.models import Sum

class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        products = Product.objects.all().order_by('name_prod')

        main_warehouse = Warehouse.objects.filter(type='main').first()
        
        # Si no hay bodega principal, devolvemos los productos con stock 0.
        if not main_warehouse:
            for p in products:
                p.total_packages = 0
                p.total_content = 0
            return products

        inventory_data = (
            Inventory.objects.filter(warehouse=main_warehouse)
            .values('product_id') # Agrupamos por el ID del producto
            .annotate(
                total_packages=Sum('quantity_packages'),
                total_content=Sum('total_content'),
                
            )
        )

        # 4. 📇 Crea un 'diccionario' de totales para una búsqueda súper rápida.
        # La clave es el ID del producto y el valor es su stock.
        totals = {
            item['product_id']: {
                'packages': item['total_packages'] or 0,
                'content': item['total_content'] or 0
            }
            for item in inventory_data
        }

        # 5. 🔗 Asigna el stock a cada producto en la lista.
        # Si un producto no está en el diccionario 'totals', se le asignará 0.
        for p in products:
            # Usamos p.product_id porque así se llama tu llave primaria.
            product_totals = totals.get(p.product_id, {'packages': 0, 'content': 0})
            p.total_packages = product_totals['packages']
            p.total_content = product_totals['content']
            p.unit_type = p.presentation.content_unit

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

