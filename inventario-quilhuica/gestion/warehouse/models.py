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

from django.db import models

class Equipment(models.Model):
    """Equipos de riego asociados a una caseta."""
    caseta = models.ForeignKey('Warehouse', on_delete=models.CASCADE, related_name='equipos')
    
    nombre_equipo = models.CharField(
        max_length=50,
        help_text="Nombre del equipo (Ej: 'A Cítricos', 'Equipo 2', 'Paltos A')"
    )
    codigo_interno = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Código opcional interno o alias corto del equipo"
    )
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['caseta__name_ware', 'nombre_equipo']
        unique_together = ('caseta', 'nombre_equipo')

    def __str__(self):
        return f"{self.nombre_equipo} ({self.caseta.name_ware})"


class Sector(models.Model):
    """Sectores físicos asociados a un equipo."""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='sectores')
    sector_num = models.PositiveIntegerField(help_text="Número de sector dentro del equipo")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['equipment__nombre_equipo', 'sector_num']
        unique_together = ('equipment', 'sector_num')

    def __str__(self):
        return f"Sector {self.sector_num} · {self.equipment.nombre_equipo}"
