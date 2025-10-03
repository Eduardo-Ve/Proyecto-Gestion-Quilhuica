from django.contrib import admin
from .models import Warehouse

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name_ware', 'type', 'created_at')
    list_filter = ('type',)
    search_fields = ('name_ware',)