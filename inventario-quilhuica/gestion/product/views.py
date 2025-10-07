from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, ListView, DeleteView
from .models import Product
from .forms import ProductForm, CategoryForm, PresentationFormSet

# --- LISTADO ---
class ProductListView(ListView):
    model = Product
    template_name = "product/product_list.html"
    context_object_name = "products"
    paginate_by = 20

# --- CREAR ---
class ProductCreateView(View):
    template_name = "product/product_form.html"
    success_url = reverse_lazy("product:product_list")

    def get(self, request, *args, **kwargs):
        product_form = ProductForm()
        category_form = CategoryForm(prefix="cat")
        formset = PresentationFormSet()
        return render(request, self.template_name, {
            "form": product_form,
            "category_form": category_form,
            "formset": formset,
            "create_mode": True,
        })

    def post(self, request, *args, **kwargs):
        product_form = ProductForm(request.POST)
        category_form = CategoryForm(request.POST, prefix="cat")
        formset = PresentationFormSet(request.POST)
        create_new_category = request.POST.get("create_new_category") == "on"

        forms_are_valid = product_form.is_valid() and formset.is_valid()
        if create_new_category:
            forms_are_valid = forms_are_valid and category_form.is_valid()
        if not forms_are_valid:
            return render(request, self.template_name, {
                "form": product_form,
                "category_form": category_form,
                "formset": formset,
                "create_mode": True,
            }, status=400)

        if create_new_category:
            category = category_form.save()
            product = product_form.save(commit=False)
            product.category = category
            product.save()
        else:
            product = product_form.save()

        formset.instance = product
        formset.save()
        return redirect(self.success_url)

# --- EDITAR ---
class ProductUpdateView(View):
    template_name = "product/product_form.html"
    success_url = reverse_lazy("product:product_list")

    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        product_form = ProductForm(instance=product)
        category_form = CategoryForm(prefix="cat")
        formset = PresentationFormSet(instance=product)
        return render(request, self.template_name, {
            "form": product_form,
            "category_form": category_form,
            "formset": formset,
            "create_mode": False,
            "object": product,
        })

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        product_form = ProductForm(request.POST, instance=product)
        category_form = CategoryForm(request.POST, prefix="cat")
        formset = PresentationFormSet(request.POST, instance=product)
        create_new_category = request.POST.get("create_new_category") == "on"

        forms_are_valid = product_form.is_valid() and formset.is_valid()
        if create_new_category:
            forms_are_valid = forms_are_valid and category_form.is_valid()
        if not forms_are_valid:
            return render(request, self.template_name, {
                "form": product_form,
                "category_form": category_form,
                "formset": formset,
                "create_mode": False,
                "object": product,
            }, status=400)

        if create_new_category:
            category = category_form.save()
            prod = product_form.save(commit=False)
            prod.category = category
            prod.save()
        else:
            prod = product_form.save()

        formset.instance = prod
        formset.save()
        return redirect(self.success_url)

# --- ELIMINAR ---
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product/product_confirm_delete.html"
    success_url = reverse_lazy("product:product_list")