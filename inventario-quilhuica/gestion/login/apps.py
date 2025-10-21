from django.apps import AppConfig


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'
    def ready(self):
            # Importa las señales aquí para que se registren
            # cuando Django inicie
            import login.signals