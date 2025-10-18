from django.utils import timezone
from datetime import timedelta
from warehouse.models import Inventory
from product.models import Product
from .models import Notification
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

LOW_STOCK_THRESHOLD = 100
EXPIRING_DAYS = 60
SNOOZE_DAYS = 1 # Días de pausa DESPUÉS de leerla

def create_notifications():
    today = timezone.now()
    two_months = today.date() + timedelta(days=EXPIRING_DAYS)
    # Límite para la pausa (solo revisa notificaciones leídas en los últimos X días)
    snooze_limit = today - timedelta(days=SNOOZE_DAYS) 

    # --- ARREGLO 1: Consulta de Administradores Corregida ---
    # Buscamos usuarios que sean 'staff' O que tengan el rol 'Administrador'
    admins = User.objects.filter(
        Q(is_staff=True) | Q(roles__name_role='Administrador')
    ).distinct() # .distinct() por si un staff también es Admin

    if not admins.exists():
        return # No hacer nada si no hay administradores

    # --- Lógica de "Bajo Stock" ---
    low_stock_items = Inventory.objects.filter(total_content__lt=LOW_STOCK_THRESHOLD)
    
    for item in low_stock_items:
        for admin in admins:
            # --- ARREGLO 3: Lógica de Pausa Corregida ---
            # Guardia 1: ¿Ya existe una notificación SIN LEER sobre esto?
            unread_exists = Notification.objects.filter(
                user=admin, product=item.product, notif_type='low_stock', read=False
            ).exists()

            # Guardia 2: ¿Hay una notificación LEÍDA recientemente (en pausa)?
            snoozed = Notification.objects.filter(
                user=admin, product=item.product, notif_type='low_stock',
                read=True, read_at__gte=snooze_limit # Revisa si se LEYÓ después del límite
            ).exists()

            # Solo crear si NO hay una sin leer Y NO está en pausa
            if not unread_exists and not snoozed:
                message = f"Producto: {item.product.name_prod} - Paquetes: {item.quantity_packages} - Caseta: {item.warehouse.name_ware} - Cantidad total Restante: {item.total_content}"
                Notification.objects.create(
                    user=admin,
                    notif_type='low_stock',
                    product=item.product,
                    warehouse=item,
                    message=message
                )

    # --- Lógica de "Próximos a Vencer" (con misma lógica de pausa) ---
    expiring_products = Product.objects.filter(expire_at__date__lte=two_months)
    for prod in expiring_products:
        for admin in admins:
            unread_exists = Notification.objects.filter(
                user=admin, product=prod, notif_type='expiring', read=False
            ).exists()
            snoozed = Notification.objects.filter(
                user=admin, product=prod, notif_type='expiring',
                read=True, read_at__gte=snooze_limit
            ).exists()

            if not unread_exists and not snoozed:
                message = f"Producto: {prod.name_prod} vence el {prod.expire_at.strftime('%d-%m-%Y')}"
                Notification.objects.create(
                    user=admin,
                    notif_type='expiring',
                    product=prod,
                    message=message
                )