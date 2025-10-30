# product/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm
from django.utils.decorators import method_decorator
from login.decorators import role_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import StockAddForm
from django.db.models import Sum, Value, Q, FloatField, IntegerField
from django.db.models.functions import Coalesce


class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        """
        Filtra los productos según el tipo de bodega (principal o caseta asignada)
        y calcula los totales de stock.
        """
        user = self.request.user
        
        # 1. Queryset base con relaciones precargadas
        queryset = Product.objects.prefetch_related('category', 'presentation')

        # 2. Validar autenticación
        if not user.is_authenticated:
            return queryset.none()

        # 3. Filtro por tipo de bodega
        if user.is_admin:
            # Admin ve la bodega principal
            warehouse_filter = Q(inventory__warehouse__type='main')
        elif user.caseta_asignada:
            # Encargado de caseta ve solo su caseta
            warehouse_filter = Q(inventory__warehouse=user.caseta_asignada)
        else:
            return queryset.none()

        # 4. Filtrar productos por bodega/caseta
        queryset = queryset.filter(warehouse_filter)

        # 5. Anotar totales (sumatorias de stock)
        queryset = queryset.annotate(
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

@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_create_form.html'
    success_url = reverse_lazy('product:product_list')

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_update_form.html'
    success_url = reverse_lazy('product:product_list')


@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = reverse_lazy('product:product_list')

@method_decorator(role_required(allowed_roles=['Administrador']), name='dispatch')
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