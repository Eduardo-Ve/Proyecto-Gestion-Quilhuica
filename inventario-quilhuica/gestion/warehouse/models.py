from django.db import models
from django.conf import settings
from product.models import Product, Presentation

#CLASE PARA BODEGA Y CASETAS.
class Warehouse(models.Model):
    name_ware = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=50,
        choices=[('main', 'Bodega Principal'), ('shed', 'Caseta')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name_ware} ({self.type})"


class Movement(models.Model):
    MOVEMENT_CHOICES = [
        ('entrada', 'Entrada'),
        ('traslado', 'Traslado'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    ware_origin = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_origin')
    ware_destin = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='movements_destin')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.IntegerField()
    moved_at = models.DateTimeField(auto_now_add=True)
    moved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.movement_type} de {self.product.name_prod} ({self.quantity})"



class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    warehouse  = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity_packages = models.FloatField(default=0)
    total_content = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'presentation', 'warehouse')

    def __str__(self):
        return f"{self.product.name_prod} ({self.quantity_packages} unidades en {self.warehouse.name_ware})"
    def save(self, *args, **kwargs):
        """Actualizar total_content automáticamente"""
        if self.presentation:
            self.total_content = self.quantity_packages * self.presentation.content_value
        super().save(*args, **kwargs)