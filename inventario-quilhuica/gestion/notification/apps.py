from django.apps import AppConfig
import sys

class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
            if 'runserver' in sys.argv:
                from . import jobs
                jobs.start()