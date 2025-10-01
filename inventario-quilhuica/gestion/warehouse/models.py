from django.db import models
from django.conf import settings
from product.models import Product, Presentation

class Warehouse(models.Model):
    name_ware = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50)  # main, shed, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_ware


class Movement(models.Model):
    MOVE_TYPES = [
        ('entrada', 'Entrada'),
        ('traslado', 'Traslado'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    ware_origin = models.ForeignKey(
        Warehouse, related_name="movements_origin", on_delete=models.SET_NULL, null=True, blank=True
    )
    ware_destin = models.ForeignKey(
        Warehouse, related_name="movements_destin", on_delete=models.CASCADE
    )
    movement_type = models.CharField(max_length=20, choices=MOVE_TYPES)
    quantity = models.FloatField()
    moved_at = models.DateTimeField(auto_now_add=True)
    moved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.movement_type} - {self.product.name_prod} ({self.quantity})"


class InventorySummary(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    ware = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity_packages = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'presentation', 'ware')

    def __str__(self):
        return f"{self.product.name_prod} ({self.quantity_packages} unidades en {self.ware.name_ware})"
