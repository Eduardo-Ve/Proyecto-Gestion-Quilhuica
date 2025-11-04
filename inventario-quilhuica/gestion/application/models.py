from django.db import models
from django.conf import settings
from product.models import Product
from warehouse.models import Warehouse, Equipment, Sector

class Application(models.Model):
    ware = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    applied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Aplicación #{self.id} - {self.ware.name_ware}"

class ApplicationDetail(models.Model):
    application = models.ForeignKey(Application, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_packages = models.FloatField()

    def __str__(self):
        return f"{self.product.name_prod} - {self.quantity_packages} unidades"
