from django.db import models
from django.utils import timezone

class Caseta(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Caseta"
        verbose_name_plural = "Casetas"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    sku = models.CharField("SKU", max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    unidad = models.CharField(max_length=20, default="unid")  
    caseta = models.ForeignKey(Caseta, on_delete=models.PROTECT, related_name="productos")
    stock_minimo = models.PositiveIntegerField(default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

    @property
    def bajo_stock(self):
        return self.cantidad <= self.stock_minimo if self.stock_minimo is not None else False

    @property
    def por_vencer(self):
        return self.fecha_vencimiento and self.fecha_vencimiento <= timezone.now().date()

# Create your models here.
