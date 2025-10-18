from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from .services import create_notifications
from django.shortcuts import render
from django.utils import timezone 
@login_required
def notification_list(request):
    """
    Muestra una página con el historial de notificaciones del usuario.
    """
    # Filtramos las notificaciones solo para el usuario actual
    # y las ordenamos por fecha de creación descendente
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications
    }
    
    # Renderizamos la plantilla HTML pasándole las notificaciones
    return render(request, 'notification/notification_list.html', context)


@login_required
def check_notifications(request):
    """
    Esta vista SOLO CONSULTA y devuelve las notificaciones no leídas.
    NO las marca como leídas.
    """
    if not request.user.is_staff:
        return JsonResponse({"low_stock": [], "expiring": []})
    
    # Es recomendable mover esto a una tarea periódica (ver más abajo).
    # Pero por ahora, para que funcione, lo dejamos aquí.
    create_notifications()
    
    # Traer notificaciones no leídas
    notifs = Notification.objects.filter(user=request.user, read=False)
    
    low_stock = [n.message for n in notifs.filter(notif_type='low_stock')]
    expiring = [n.message for n in notifs.filter(notif_type='expiring')]
    
    return JsonResponse({
        "low_stock": low_stock,
        "expiring": expiring
    })

@login_required
def mark_notifications_read(request):
    """
    Marca todas las notificaciones del usuario como leídas y
    guarda la fecha y hora de la lectura.
    """
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, read=False).update(
            read=True,
            read_at=timezone.now() # ✨ AÑADE ESTA LÍNEA
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)