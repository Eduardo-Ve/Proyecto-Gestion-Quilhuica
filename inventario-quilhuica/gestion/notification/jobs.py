from apscheduler.schedulers.background import BackgroundScheduler
from .utils import send_low_stock_alert, send_monthly_summary_pdf_email
from .services import create_notifications


def check_inventory_and_create_notifications():
    print("🕘 Ejecutando revisión de inventario...")
    create_notifications()
    print("✅ Revisión finalizada.")


def start():
    scheduler = BackgroundScheduler()

    # Verificación de stock (3 veces al día)
    scheduler.add_job(
        check_inventory_and_create_notifications,
        trigger='cron',
        day_of_week='mon-fri',
        hour='9,14,17',
        minute='0',
        id='check_inventory_job',
        replace_existing=True
    )

    # Resumen mensual el último día hábil (18:00)
    scheduler.add_job(
        send_monthly_summary_pdf_email,
        trigger='cron',
        day='28-31',
        hour='18',
        minute='0',
        id='monthly_summary_job',
        replace_existing=True
    )

    scheduler.start()
    print("🚀 Scheduler iniciado: notificaciones + resumen mensual.")
