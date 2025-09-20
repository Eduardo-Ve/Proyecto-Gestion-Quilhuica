from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "categoria", "cantidad", "unidad", "stock_minimo", "fecha_vencimiento", "precio"]
