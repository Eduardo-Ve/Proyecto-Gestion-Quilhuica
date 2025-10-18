from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ApplicationDetail
from warehouse.models import Inventory

@receiver(post_save, sender=ApplicationDetail)
def update_inventory_after_application(sender, instance, created, **kwargs):
    if created:
        inventory = Inventory.objects.filter(
            product=instance.product,
            presentation=instance.presentation,
            warehouse=instance.application.ware
        ).first()

        if inventory:
            inventory.quantity_packages -= instance.quantity_packages
            inventory.save()
