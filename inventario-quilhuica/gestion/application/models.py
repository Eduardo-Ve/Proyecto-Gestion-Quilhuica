from django.db import models
from django.conf import settings
from django.apps import apps
from product.models import Product

class Application(models.Model):
    ware = models.ForeignKey(
        'warehouse.Warehouse',  
        on_delete=models.PROTECT
    )
    equipment = models.ForeignKey(
        'warehouse.Equipment',  
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    sector = models.ForeignKey(
        'warehouse.Sector',  
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"Aplicación #{self.id} - {self.ware.name_ware}"


class ApplicationDetail(models.Model):
    application = models.ForeignKey(
        Application,
        related_name='details',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity_packages = models.FloatField()

    def __str__(self):
        return f"{self.product.name_prod} - {self.quantity_packages} unidades"
