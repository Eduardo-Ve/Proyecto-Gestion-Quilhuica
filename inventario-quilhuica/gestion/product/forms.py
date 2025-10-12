from django import forms
from django.forms import inlineformset_factory
from .models import Product, Presentation, Category


class ProductForm(forms.ModelForm):
    # Campos extra para crear categoría en línea
    create_new_category = forms.BooleanField(
        required=False,
        label="Crear nueva categoría en lugar de seleccionar una existente"
    )
    new_category_name = forms.CharField(
        required=False,
        label="Nombre de categoría"
    )
    new_category_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        label="Descripción"
    )

    class Meta:
        model = Product
        fields = ["name_prod", "category"]
        widgets = {
            "name_prod": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permitimos enviar el form sin categoría si se creará una nueva
        self.fields["category"].required = False
        self.fields["category"].empty_label = "— Selecciona una categoría —"

    def clean(self):
        cleaned = super().clean()
        create_new = cleaned.get("create_new_category")
        category = cleaned.get("category")
        new_name = cleaned.get("new_category_name")

        if create_new:
            if not new_name:
                self.add_error("new_category_name", "Indica el nombre de la nueva categoría.")
        else:
            if not category:
                self.add_error("category", "Selecciona una categoría o marca 'Crear nueva categoría'.")
        return cleaned

    def save(self, commit=True):
        # Si se marcó crear nueva categoría, la creamos y asignamos
        if self.cleaned_data.get("create_new_category"):
            name = self.cleaned_data.get("new_category_name")
            desc = self.cleaned_data.get("new_category_description", "")
            category = Category.objects.create(name_cat=name, description_cat=desc)
            self.instance.category = category
        return super().save(commit=commit)


class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ["package_type", "content_value", "content_unit"]
        labels = {
            "package_type": "Tipo de envase",
            "content_value": "Cantidad",
            "content_unit": "Unidad",
        }
        widgets = {
            "package_type": forms.Select(attrs={"class": "form-select"}),
            "content_value": forms.NumberInput(attrs={"class": "form-control", "step": "any", "min": "0"}),
            "content_unit": forms.Select(attrs={"class": "form-select"}),
        }

PresentationFormSet = inlineformset_factory(
    parent_model=Product,
    model=Presentation,
    form=PresentationForm,
    extra=0,
    can_delete=False,
    min_num=1,             
    validate_min=True,
)
