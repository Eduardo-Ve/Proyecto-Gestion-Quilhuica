from django.contrib import admin
from .models import Category, Product, Presentation

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "name_cat", "created_at")
    search_fields = ("name_cat",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name_prod", "category", "added_at")
    list_filter = ("category",)
    search_fields = ("name_prod",)

@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ("presentation_id", "product", "package_type", "content_value", "content_unit")
    list_filter = ("package_type", "content_unit")
    search_fields = ("product__name_prod",)

