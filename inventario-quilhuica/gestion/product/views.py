from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db import transaction
from .models import Product
from .forms import ProductForm, PresentationFormSet   
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.db.models import F, Sum, DecimalField, ExpressionWrapper, Prefetch
from django.views.generic import ListView
from .models import Product, Presentation
# --- LISTADO ---
class ProductListView(ListView):
    model = Product
    template_name = "product/product_list.html"
    context_object_name = "products"
    paginate_by = 20

# --- CREAR ---
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "product/product_form.html"
    success_url = reverse_lazy("product:product_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = PresentationFormSet(self.request.POST)
        else:
            ctx["formset"] = PresentationFormSet()
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx["formset"]
        with transaction.atomic():
            self.object = form.save() 
            formset.instance = self.object
            if formset.is_valid():
                formset.save()
            else:
                return self.form_invalid(form)
        return super().form_valid(form)

# --- EDITAR ---
class ProductUpdateView(View):
    template_name = "product/product_form.html"
    success_url = reverse_lazy("product:product_list")

    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        formset = PresentationFormSet(instance=product)
        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "create_mode": False,
            "object": product,
        })

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, instance=product)
        formset = PresentationFormSet(request.POST, instance=product)

        if not (form.is_valid() and formset.is_valid()):
            return render(request, self.template_name, {
                "form": form,
                "formset": formset,
                "create_mode": False,
                "object": product,
            }, status=400)

        # ProductForm ya maneja crear categoría nueva si viene marcado
        with transaction.atomic():
            prod = form.save()
            formset.instance = prod
            formset.save()

        return redirect(self.success_url)

# --- ELIMINAR ---
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product/product_confirm_delete.html"
    success_url = reverse_lazy("product:product_list")


