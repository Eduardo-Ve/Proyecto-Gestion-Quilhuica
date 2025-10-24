from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm
from warehouse.models import * 
from django.db.models import Sum
from django.utils.decorators import method_decorator
from login.decorators import role_required
class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        user = self.request.user
        products = Product.objects.all().order_by('name_prod')

        # Si el usuario es un administrador, se muestran los productos de la bodega principal
        if user.is_authenticated and user.is_admin:
            main_warehouse = Warehouse.objects.filter(type='main').first()

            if not main_warehouse:
                for p in products:
                    p.total_packages = 0
                    p.total_content = 0
                return products

            inventory_data = (
                Inventory.objects.filter(warehouse=main_warehouse)
                .values('product_id')
                .annotate(
                    total_packages=Sum('quantity_packages'),
                    total_content=Sum('total_content'),
                )
            )

            totals = {
                item['product_id']: {
                    'packages': item['total_packages'] or 0,
                    'content': item['total_content'] or 0
                }
                for item in inventory_data
            }

            for p in products:
                product_totals = totals.get(p.product_id, {'packages': 0, 'content': 0})
                p.total_packages = product_totals['packages']
                p.total_content = product_totals['content']
                p.unit_type = p.presentation.content_unit

            return products

        # Si el usuario es encargado de una caseta, se muestran los productos de su caseta asignada
        elif user.is_authenticated and hasattr(user, 'caseta_asignada'):
            assigned_warehouse = user.caseta_asignada
            inventory_data = (
                Inventory.objects.filter(warehouse=assigned_warehouse)
                .values('product_id')
                .annotate(
                    total_packages=Sum('quantity_packages'),
                    total_content=Sum('total_content'),
                )
            )

            totals = {
                item['product_id']: {
                    'packages': item['total_packages'] or 0,
                    'content': item['total_content'] or 0
                }
                for item in inventory_data
            }

            for p in products:
                product_totals = totals.get(p.product_id, {'packages': 0, 'content': 0})
                p.total_packages = product_totals['packages']
                p.total_content = product_totals['content']
                p.unit_type = p.presentation.content_unit

            return products

        # Si el usuario no es admin ni encargado de caseta, no se debería mostrar nada
        else:
            return products

    
@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_create_form.html'  # Formulario de creación
    success_url = reverse_lazy('product:product_list')

    # Se reemplaza el código comentado de abajo, por la nueva función que evita que la
    # categoría se guarde dos veces.
    """def form_valid(self, form):
        
        Sobrescribe el método form_valid para pasar el usuario actual al form.save()
        
        product = form.save(user=self.request.user) # <-- 1er save()
        return super().form_valid(form)"""          # <-- 2º save() (el de CreateView)
    
    def form_valid(self, form):
        # Guardamos una sola vez y devolvemos el redirect manualmente
        self.object = form.save(user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())
    

@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_update_form.html'  # Formulario de edición
    success_url = reverse_lazy('product:product_list')

@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'  # Confirmación de eliminación
    success_url = reverse_lazy('product:product_list')