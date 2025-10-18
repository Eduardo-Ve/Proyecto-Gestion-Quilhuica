# notification/management/commands/check_inventory.py

from django.core.management.base import BaseCommand
from notification.services import create_notifications # Asegúrate que la ruta de importación sea correcta

class Command(BaseCommand):
    help = 'Revisa el inventario y crea las notificaciones de bajo stock o vencimiento.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando la revisión de inventario para crear notificaciones...'))
        
        # Llama a tu función de servicio que contiene toda la lógica
        create_notifications() 
        
        self.stdout.write(self.style.SUCCESS('Revisión de inventario completada.'))