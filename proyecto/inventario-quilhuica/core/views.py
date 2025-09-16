from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Producto
from .forms import ProductoForm

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "core/producto_list.html"
    context_object_name = "productos"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q) | qs.filter(sku__icontains=q)
        return qs

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "core/producto_form.html"
    success_url = reverse_lazy("core:producto_list")

class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "core/producto_form.html"
    success_url = reverse_lazy("core:producto_list")

class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = "core/producto_confirm_delete.html"
    success_url = reverse_lazy("core:producto_list")

# Create your views here.
