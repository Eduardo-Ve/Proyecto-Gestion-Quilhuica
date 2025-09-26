from django import forms
from django.forms import inlineformset_factory
from .models import Category, Product, Presentation


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name_cat", "description_cat"]
        widgets = {
            "name_cat": forms.TextInput(attrs={"class": "form-control"}),
            "description_cat": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name_prod", "category"]
        widgets = {
            "name_prod": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

    # Opcional: placeholder para guiar al usuario
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = "— Selecciona una categoría —"


PresentationFormSet = inlineformset_factory(
    parent_model=Product,
    model=Presentation,
    fields=["package_type", "content_value", "content_unit"],
    extra=1,
    can_delete=True,
    widgets={
        "package_type": forms.Select(attrs={"class": "form-select"}),
        "content_value": forms.NumberInput(attrs={"class": "form-control", "step": "any", "min": "0"}),
        "content_unit": forms.Select(attrs={"class": "form-select"}),
    }
)

