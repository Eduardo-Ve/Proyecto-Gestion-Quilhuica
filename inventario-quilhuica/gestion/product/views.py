from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Product
from .forms import ProductForm, StockAddForm
from login.decorators import role_required
from login.utils import user_can
from django.db.models import Q, Sum, Value, FloatField, IntegerField
from django.db.models.functions import Coalesce


#  LISTADO GENERAL DE PRODUCTOS
class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.prefetch_related('category', 'presentation')

        if not user.is_authenticated:
            return queryset.none()

        # Admin o Supervisor: todo el inventario principal
        if user.is_admin or user.has_role("Supervisor"):
            warehouse_filter = Q(inventory__warehouse__type='main')

        # Encargado de Caseta: solo sus casetas
        elif user.ware_assig.exists():
            warehouse_filter = Q(inventory__warehouse__in=user.ware_assig.all())
        else:
            return queryset.none()

        queryset = queryset.filter(warehouse_filter).annotate(
            total_packages=Coalesce(
                Sum('inventory__quantity_packages', filter=warehouse_filter),
                Value(0),
                output_field=IntegerField()
            ),
            total_content=Coalesce(
                Sum('inventory__total_content', filter=warehouse_filter),
                Value(0.0),
                output_field=FloatField()
            )
        ).distinct().order_by('name_prod')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["puede_crear"] = user_can(user, "producto", "create")
        context["puede_editar"] = user_can(user, "producto", "edit")
        context["puede_eliminar"] = user_can(user, "producto", "delete")

        if user.has_role("Encargado de Caseta") and user.ware_assig.exists():
            casetas_data = []
            for caseta in user.ware_assig.all():
                products = (
                    Product.objects.filter(inventory__warehouse=caseta)
                    .prefetch_related('category', 'presentation')
                    .annotate(
                        total_packages=Coalesce(
                            Sum('inventory__quantity_packages', filter=Q(inventory__warehouse=caseta)),
                            Value(0),
                            output_field=IntegerField()
                        ),
                        total_content=Coalesce(
                            Sum('inventory__total_content', filter=Q(inventory__warehouse=caseta)),
                            Value(0.0),
                            output_field=FloatField()
                        )
                    )
                    .distinct()
                    .order_by('name_prod')
                )
                casetas_data.append({'caseta': caseta, 'productos': products})
            context['casetas_data'] = casetas_data

        return context


#  CREAR / EDITAR PRODUCTO
@method_decorator(role_required(allowed_roles=['Administrador', 'Supervisor']), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_create_form.html'
    success_url = reverse_lazy('product:product_list')


@method_decorator(role_required(allowed_roles=['Administrador', 'Supervisor']), name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_update_form.html'
    success_url = reverse_lazy('product:product_list')


#  DESACTIVAR (Soft Delete)
@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
class ProductDeleteView(View):
    """Desactiva un producto en lugar de eliminarlo físicamente."""

    def post(self, request, pk):
        product = get_object_or_404(Product.objects_all, pk=pk)
        if not product.is_active:
            messages.warning(request, f"El producto '{product.name_prod}' ya está desactivado.")
        else:
            product.is_active = False
            product.save(update_fields=['is_active'])
            messages.success(
                request,
                f"Producto '{product.name_prod}' desactivado correctamente. "
        
            )
        return redirect(reverse_lazy('product:product_list'))

    def get(self, request, pk):
        product = get_object_or_404(Product.objects_all, pk=pk)
        return render(request, 'product/product_confirm_delete.html', {'product': product})


#  AÑADIR STOCK
@method_decorator(role_required(allowed_roles=['Administrador', 'Supervisor']), name='dispatch')
class StockAddView(CreateView):
    template_name = 'product/add_stock_form.html'
    form_class = StockAddForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Stock añadido correctamente.")
            return redirect('product:product_list')
        return render(request, self.template_name, {'form': form})


#  LISTA DE PRODUCTOS DESACTIVADOS
@login_required
@role_required(allowed_roles=['Administrador'])
def product_inactive_list(request):
    productos = Product.objects_all.filter(is_active=False).order_by('name_prod')
    context = {
        'productos': productos,
        'title': 'Productos Desactivados'
    }
    return render(request, 'product/product_inactive_list.html', context)


#  REACTIVAR PRODUCTO
@login_required
@role_required(allowed_roles=['Administrador'])
def product_reactivate(request, pk):
    product = get_object_or_404(Product.objects_all, pk=pk)

    if product.is_active:
        messages.info(request, f"El producto '{product.name_prod}' ya estaba activo.")
    else:
        product.is_active = True
        product.save(update_fields=['is_active'])
        messages.success(request, f"Producto '{product.name_prod}' reactivado correctamente.")
    
    return redirect(reverse_lazy('product:product_inactive_list'))
