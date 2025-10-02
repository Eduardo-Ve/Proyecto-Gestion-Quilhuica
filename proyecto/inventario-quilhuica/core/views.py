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
    template_name = "core/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        total_value_expr = ExpressionWrapper(
            F("stock_units") * F("content_value"),
            output_field=DecimalField(max_digits=14, decimal_places=2)
        )
        pres_qs = Presentation.objects.annotate(total_value=total_value_expr)
        return (
            Product.objects
            .select_related("category")
            .prefetch_related(Prefetch("presentations", queryset=pres_qs))
            .order_by("name_prod")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # añade al objeto product un dict con totales por unidad
        for p in ctx["products"]:
            acc = {}
            for pres in p.presentations.all():
                unit = pres.content_unit
                acc[unit] = acc.get(unit, 0) + (pres.stock_units or 0) * (pres.content_value or 0)
            p.totals_by_unit = acc  # <— ahora se puede acceder como p.totals_by_unit en el template
        return ctx

# --- CREAR ---
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("core:product_list")

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
            self.object = form.save()  # crea categoría nueva si corresponde
            formset.instance = self.object
            if formset.is_valid():
                formset.save()
            else:
                return self.form_invalid(form)
        return super().form_valid(form)

# --- EDITAR ---
class ProductUpdateView(View):
    template_name = "core/product_form.html"
    success_url = reverse_lazy("core:product_list")

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
    template_name = "core/product_confirm_delete.html"
    success_url = reverse_lazy("core:product_list")


