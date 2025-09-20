from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    categoria = models.CharField(max_length=80, blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad = models.CharField(max_length=20, default="unid")  # ej: kg, lt, unid
    caseta = models.CharField(max_length=50, blank=True)      # ubicación
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
