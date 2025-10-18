# notification/jobs.py

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from .utils import send_low_stock_alert 
from .services import create_notifications # Importa la función que ya tienes

def check_stock_job():
    """
    Esta es la función que se ejecutará en segundo plano.
    """
    print("--- Ejecutando tarea programada: Verificando stock bajo... ---")
    send_low_stock_alert()
    print("--- Tarea finalizada. ---")

def check_inventory_and_create_notifications():
    """
    Esta es la función que se ejecutará en segundo plano.
    Llama al servicio que revisa el inventario y crea las notificaciones 
    en la base de datos si es necesario.
    """
    print("--- Ejecutando tarea programada: Verificando inventario... ---")
    create_notifications() 
    print("--- Tarea finalizada. ---")

def start():
    """
    La función que inicia el programador de tareas.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_inventory_and_create_notifications,
        trigger='cron',
        day_of_week='mon-fri',
        hour='9,14,17', # A las 9:00, 14:00 y 17:00
        minute='0',
        id='check_inventory_job', # ID único para la tarea
        replace_existing=True
    )    
    # schedule='cron' es para programar en momentos específicos
    # day_of_week='mon-fri' -> Lunes a Viernes
    # hour='9,14,17' -> A las 9 AM, 2 PM (14h) y 5 PM (17h)
    # minute='0' -> En el minuto 0 de esas horas
    print("Scheduler iniciado... La revisión de inventario está programada.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

