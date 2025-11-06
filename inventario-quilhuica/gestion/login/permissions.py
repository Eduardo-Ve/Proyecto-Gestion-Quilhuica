# login/permissions.py

ROLE_PERMISSIONS = {
    "Administrador": {
        "caseta": {"create": True, "edit": True, "delete": True, "view": True},
        "producto": {"create": True, "edit": True, "delete": True, "view": True},
        "stock": {"create": True, "edit": True, "delete": True, "view": True},
        "aplicacion": {"create": True, "edit": True, "delete": True, "view": True},
    },
    "Supervisor": {
        "caseta": {"create": True, "edit": True, "delete": False, "view": True},
        "producto": {"create": True, "edit": True, "delete": False, "view": True},
        "stock": {"create": True, "edit": True, "delete": False, "view": True},
        "aplicacion": {"create": True, "edit": True, "delete": False, "view": True},
    },
    "Encargado de Caseta": {
        "caseta": {"create": False, "edit": False, "delete": False, "view": True},
        "producto": {"create": False, "edit": False, "delete": False, "view": True},
        "stock": {"create": True, "edit": False, "delete": False, "view": True},
        "aplicacion": {"create": True, "edit": False, "delete": False, "view": True},
    },
    
}
