from django.db.models.signals import post_save
from django.dispatch import receiver
from product.models import Product, Presentation
from warehouse.models import Inventory, Warehouse

@receiver(post_save, sender=Product)
def create_inventory_in_main_warehouse(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo producto, se agrega al inventario
    de la bodega principal con cantidad 0.
    """
    if created:
        try:
            # Buscar la bodega principal
            main_warehouse = Warehouse.objects.filter(type='main').first()
            if not main_warehouse:
                print("⚠️ No se encontró una bodega principal registrada.")
                return

            # Si el producto tiene presentaciones asociadas
            presentations = Presentation.objects.filter(product=instance)
            if not presentations.exists():
                print(f"⚠️ El producto '{instance.name_prod}' no tiene presentaciones.")
                return

            for presentation in presentations:
                Inventory.objects.get_or_create(
                    product=instance,
                    presentation=presentation,
                    warehouse=main_warehouse,
                    defaults={'quantity_packages': 0}
                )
            print(f"✅ Inventario creado automáticamente para '{instance.name_prod}' en bodega principal.")
        except Exception as e:
            print(f"❌ Error creando inventario automático: {e}")