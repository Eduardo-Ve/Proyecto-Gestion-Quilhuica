from django.contrib import admin
from .models import Producto, Caseta

@admin.register(Caseta)
class CasetaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("sku", "nombre", "caseta", "cantidad", "stock_minimo", "fecha_vencimiento", "bajo_stock")
    list_filter = ("caseta", "fecha_vencimiento")
    search_fields = ("sku", "nombre", "descripcion")

# Register your models here.
