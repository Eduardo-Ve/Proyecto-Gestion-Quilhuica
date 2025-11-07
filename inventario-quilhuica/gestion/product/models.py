# product/models.py
from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name_cat = models.CharField(max_length=120)
    description_cat = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name_cat']

    def __str__(self):
        return self.name_cat


class Presentation(models.Model):
    PACKAGE_CHOICES = [
        ('saco', 'Saco'),
        ('bidon', 'Bidón'),
        ('caja', 'Caja'),
        ('paquete', 'Paquete'),
    ]
    UNIT_CHOICES = [
        ('kg', 'Kilogramos'),
        ('litros', 'Litros'),
    ]

    presentation_id = models.AutoField(primary_key=True)
    package_type = models.CharField(max_length=10, choices=PACKAGE_CHOICES)
    content_value = models.FloatField()
    content_unit = models.CharField(max_length=10, choices=UNIT_CHOICES)

    class Meta:
        ordering = ['package_type', 'content_value']

    def __str__(self):
        return f"{self.package_type} {self.content_value} {self.content_unit}"


# --- Managers para ocultar desactivados por defecto ---
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name_prod = models.CharField(max_length=120)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
    )
    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.PROTECT,
        related_name='products',
    )
    added_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()

    # 🔹 Soft delete
    is_active = models.BooleanField(default=True)

    # Managers
    objects = ProductManager()               # por defecto, solo activos
    objects_all = models.Manager()           # acceso a todos (incl. inactivos)
    qs = ProductQuerySet.as_manager()        # para usar .active() si quieres

    class Meta:
        ordering = ['name_prod']

    def __str__(self):
        estado = "" if self.is_active else " (inactivo)"
        return f"{self.name_prod}{estado}"
