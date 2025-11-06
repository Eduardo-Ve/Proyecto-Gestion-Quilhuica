# login/utils.py
from .permissions import ROLE_PERMISSIONS

def user_can(user, module, action):
    """
    Verifica si el usuario tiene permiso para realizar una acción sobre un módulo.
    Basado en sus roles definidos en ROLE_PERMISSIONS.
    """
    if not user.is_authenticated:
        return False

    # El superusuario siempre tiene todos los permisos
    if user.is_superuser:
        return True

    try:
        user_roles = getattr(user, "roles", None)
        if not user_roles:
            return False

        for role in user_roles.all():
            role_name = role.name_role.strip()  # 🔹 usa el campo correcto
            role_perms = ROLE_PERMISSIONS.get(role_name, {})
            module_perms = role_perms.get(module, {})
            if module_perms.get(action, False):
                return True

    except Exception as e:
        print(f"[DEBUG user_can] Error evaluando permisos: {e}")

    return False
