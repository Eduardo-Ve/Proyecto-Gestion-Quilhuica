from django.db import models
from django.conf import settings
from warehouse.models import Inventory
from product.models import Product

class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('low_stock', 'Bajo Stock'),
        ('expiring', 'Próximo a Vencer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_notif_type_display()} - {self.product.name_prod}"