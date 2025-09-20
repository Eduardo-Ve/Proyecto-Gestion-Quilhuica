from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre","categoria","cantidad","unidad","stock_minimo","fecha_vencimiento","precio")
    search_fields = ("nombre","categoria")
    list_filter = ("categoria",)
