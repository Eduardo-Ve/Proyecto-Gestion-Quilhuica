from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = "core/product_list.html"
    context_object_name = "products"
    paginate_by = 20

class ProductCreateView(CreateView):
    model = Product
    fields = ["name_prod", "category"]  # added_at es auto
    template_name = "core/product_form.html"
    success_url = reverse_lazy("core:product_list")

class ProductUpdateView(UpdateView):
    model = Product
    fields = ["name_prod", "category"]
    template_name = "core/product_form.html"
    success_url = reverse_lazy("core:product_list")

class ProductDeleteView(DeleteView):
    model = Product
    template_name = "core/product_confirm_delete.html"
    success_url = reverse_lazy("core:product_list")
