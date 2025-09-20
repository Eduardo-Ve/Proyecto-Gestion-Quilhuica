from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Producto
from .forms import ProductoForm

class ProductoListView(ListView):
    model = Producto
    template_name = "core/producto_list.html"
    context_object_name = "productos"

class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "core/producto_form.html"
    success_url = reverse_lazy("core:producto_list")

class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "core/producto_form.html"
    success_url = reverse_lazy("core:producto_list")

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = "core/producto_confirm_delete.html"
    success_url = reverse_lazy("core:producto_list")
