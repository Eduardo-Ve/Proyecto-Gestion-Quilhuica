from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware que bloquea el acceso a todas las vistas
    excepto las de login y admin, si el usuario no está autenticado.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            reverse('login'),      # Vista de login (de igual manera deberiamos mostrar una pagina como de No autorizado o algo asi xd)
            reverse('admin:login'), 
            '/admin/',             # Panel de administración del Django
        ]

    def __call__(self, request):
        # Si el usuario no está autenticado
        if not request.user.is_authenticated:
            path = request.path_info
            if not any(path.startswith(url) for url in self.exempt_urls):
                return redirect('login')  # Redirige al login
        return self.get_response(request)
