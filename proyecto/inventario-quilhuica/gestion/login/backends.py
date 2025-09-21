from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import Usuario

class UsuarioBackend(ModelBackend):
    """
    Permite login usando nombre_usuario o correo.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(
                Q(nombre_usuario__iexact=username) | Q(correo__iexact=username)
            )
            if user.check_password(password):
                return user
        except Usuario.DoesNotExist:
            return None
