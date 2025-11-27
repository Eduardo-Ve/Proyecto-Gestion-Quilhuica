from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


#  MODELOS DE BODEGAS Y CASETAS
class Warehouse(models.Model):
    name_ware = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=50,
        choices=[('main', 'Bodega Principal'), ('shed', 'Caseta')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)  # 🔸 Soft delete flag

    def __str__(self):
        return f"{self.name_ware}"

    def delete(self, *args, **kwargs):
        """Soft delete para evitar romper relaciones protegidas."""
        self.activo = False
        self.save()



#  MOVIMIENTOS
class Movement(models.Model):
    MOVEMENT_CHOICES = [
        ('entrada', 'Entrada'),
        ('traslado', 'Traslado'),
        ('salida', 'Salida'),
    ]

    # 🔸 Usa referencia por string para evitar ciclo
    product = models.ForeignKey('product.Product', on_delete=models.PROTECT)
    presentation = models.ForeignKey('product.Presentation', on_delete=models.PROTECT)

    ware_origin = models.ForeignKey(
        'self'.replace('self', 'warehouse.Warehouse'),  # alias, no se usa self realmente
        on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_origin'
    )
    ware_destin = models.ForeignKey(
        'warehouse.Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_destin'
    )

    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.FloatField()
    moved_at = models.DateTimeField(auto_now_add=True)
    moved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    def clean(self):
        if self.ware_destin and not self.ware_destin.activo:
            raise ValidationError("No se pueden registrar movimientos hacia casetas inactivas.")

    def __str__(self):
        return f"{self.movement_type} de {self.product.name_prod} ({self.quantity})"


#  INVENTARIO
class Inventory(models.Model):
    product = models.ForeignKey('product.Product', on_delete=models.PROTECT)
    presentation = models.ForeignKey('product.Presentation', on_delete=models.PROTECT)
    warehouse  = models.ForeignKey(Warehouse, on_delete=models.PROTECT)

    quantity_packages = models.IntegerField(default=0)
    total_content = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'presentation', 'warehouse')

    def __str__(self):
        return f"{self.product.name_prod} ({self.quantity_packages} unidades en {self.warehouse.name_ware})"

    def save(self, *args, **kwargs):
        if self.presentation:
            self.total_content = self.quantity_packages * self.presentation.content_value
        super().save(*args, **kwargs)


#  EQUIPOS Y SECTORES
class Equipment(models.Model):
    caseta = models.ForeignKey('warehouse.Warehouse', on_delete=models.CASCADE, related_name='equipos')
    nombre_equipo = models.CharField(max_length=50)
    codigo_interno = models.CharField(max_length=20, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['caseta__name_ware', 'nombre_equipo']
        unique_together = ('caseta', 'nombre_equipo')

    def __str__(self):
        return f"{self.nombre_equipo} ({self.caseta.name_ware})"


class Sector(models.Model):
    equipment = models.ForeignKey('warehouse.Equipment', on_delete=models.CASCADE, related_name='sectores')
    sector_num = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['equipment__nombre_equipo', 'sector_num']
        unique_together = ('equipment', 'sector_num')

    def __str__(self):
        return f"Sector {self.sector_num} · {self.equipment.nombre_equipo}"
