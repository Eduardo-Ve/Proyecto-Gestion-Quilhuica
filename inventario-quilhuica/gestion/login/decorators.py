from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.conf import settings

def role_required(allowed_roles=[]):
    """
    Decorador que restringe el acceso a usuarios que no tengan
    alguno de los roles especificados.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            
            # 1. Verificar si está autenticado
            if not request.user.is_authenticated:
                # Redirigir al login, guardando la página actual
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            
            # 2. El Superusuario siempre tiene acceso
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 3. Verificar si el usuario tiene al menos UNO de los roles permitidos
            #    Usamos el método que acabamos de crear en el modelo Usuario
            if not request.user.has_role(allowed_roles):
                # Si está autenticado pero no tiene el rol, lanzar 403 Forbidden
                raise PermissionDenied 
            
            # Si pasa todas las verificaciones, ejecutar la vista
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator