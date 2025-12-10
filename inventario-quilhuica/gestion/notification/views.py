
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from .models import Notification
from .services import create_notifications
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
            read_at=timezone.now()
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

def send_activation_email(request, user):
    subject = "Activa tu cuenta en Gestión Quilhuica"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.correo]

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_link = request.build_absolute_uri(
        reverse("activar_cuenta", kwargs={"uidb64": uidb64, "token": token})
    )

    context = {
        "nombre_usuario": user.nombre_usuario,
        "activation_link": activation_link,
        "year": timezone.now().year,
    }

    html_content = render_to_string("notification/activation_email.html", context)
    text_content = f"""
    Hola {user.nombre_usuario},

    Has sido registrado en Gestión Quilhuica.
    Para activar tu cuenta y definir tu contraseña, entra al siguiente enlace:

    {activation_link}

    Si no solicitaste este acceso, ignora este mensaje.
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
