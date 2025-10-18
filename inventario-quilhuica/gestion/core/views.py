from django.shortcuts import render

# Create your views here.
def index (request):
    return render(request, 'core/core.html', {})

def style (request):
    return render(request, 'core/style.html', {})

ERROR_MESSAGES = {
    400: "Solicitud incorrecta (Bad Request).",
    403: "No tienes permisos para acceder a esta sección.",
    404: "Página no encontrada.",
    500: "Error interno del servidor. Intenta más tarde."
}

def error_400(request, exception=None):
    return render(request, "errors/error.html", {"code": 400, "message": ERROR_MESSAGES[400]}, status=400)

def error_403(request, exception=None):
    return render(request, "errors/error.html", {"code": 403, "message": ERROR_MESSAGES[403]}, status=403)

def error_404(request, exception=None):
    return render(request, "errors/error.html", {"code": 404, "message": ERROR_MESSAGES[404]}, status=404)

def error_500(request):
    return render(request, "errors/error.html", {"code": 500, "message": ERROR_MESSAGES[500]}, status=500)


# la funcion para tomar los productos serian 
# quien(get.user) cuando(filter by date ) donde (warehouse.models inventory && Warehouse) name_warehouse,  que se aplico (get prodcuts filter applyd)