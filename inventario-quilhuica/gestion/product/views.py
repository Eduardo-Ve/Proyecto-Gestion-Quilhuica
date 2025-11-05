from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm, StockAddForm
from django.utils.decorators import method_decorator
from login.decorators import role_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum, Value, Q, FloatField, IntegerField
from django.db.models.functions import Coalesce

class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        """
        Mantiene el comportamiento original (admin o encargado),
        pero devolvemos productos globales solo para admin.
        """
        user = self.request.user
        queryset = Product.objects.prefetch_related('category', 'presentation')

        if not user.is_authenticated:
            return queryset.none()

        if user.is_admin:
            warehouse_filter = Q(inventory__warehouse__type='main')
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
        """
        Añade un contexto extra con productos agrupados por caseta
        (solo para encargados con múltiples casetas).
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if not user.is_admin and user.ware_assig.exists():
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
