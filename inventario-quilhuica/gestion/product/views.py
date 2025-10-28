# product/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm
from warehouse.models import Warehouse, Inventory
from django.db.models import Sum
from django.utils.decorators import method_decorator
from login.decorators import role_required


class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    # tu método get_queryset aquí (el que ya corregimos antes)
    # ...


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
