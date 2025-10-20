from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from .services import create_notifications
from django.shortcuts import render
from django.utils import timezone 
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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


def send_welcome_email(user, temp_password):
    """Envía correo de bienvenida con contraseña temporal."""
    subject = "Bienvenido a Gestión Quilhuica"
    from_email = "no-reply@quilhuica.cl"
    to = [user.correo]

    context = {
        'nombre_usuario': user.nombre_usuario,
        'temp_password': temp_password,
        'login_url': "http://127.0.0.1:8000/",  # cambiar por el dominio cuando temos en producción
        'year': timezone.now().year,
    }

    html_content = render_to_string("notification/welcome_email.html", context)
    text_content = f"""
    Hola {user.nombre_usuario},

    Tu cuenta ha sido creada exitosamente en Gestión Quilhuica.
    Tu contraseña temporal es: {temp_password}

    Al iniciar sesión se te pedirá cambiarla.

    Ingresa aquí: http://127.0.0.1:8000/
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()