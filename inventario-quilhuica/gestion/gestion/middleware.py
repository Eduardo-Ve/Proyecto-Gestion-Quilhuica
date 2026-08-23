from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    """
    Middleware que bloquea el acceso a todas las vistas
    excepto las exentas si el usuario no está autenticado.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Rutas que NO requieren autenticación
        self.exempt_paths = [
            '/admin/',
            '/login/',
            '/register/',
            '/reset_password/',
            '/reset_password_sent/',
            '/reset/',
            '/reset_password_complete/',
            '/cambiar-contrasena-inicial/',
            '/static'
        ]

    def __call__(self, request):
        # Permitir acceso a las URLs exentas
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)

        # Si el usuario no está autenticado, redirigir a login
        if not request.user.is_authenticated:
            return redirect('login')

        return self.get_response(request)
