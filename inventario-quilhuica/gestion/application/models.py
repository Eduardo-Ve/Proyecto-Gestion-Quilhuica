from django.db import models
from django.conf import settings
from product.models import Product, Presentation
from warehouse.models import Warehouse

class Application(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    ware = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity_packages = models.FloatField()
    applied_at = models.DateTimeField(auto_now_add=True)
    applied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Aplicación {self.product.name_prod} - {self.quantity_packages} unidades"
