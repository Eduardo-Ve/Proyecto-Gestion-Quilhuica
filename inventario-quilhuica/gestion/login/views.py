from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth import (
    logout,
    login as auth_login,
    update_session_auth_hash,
    get_user_model,
)
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from django.urls import reverse, reverse_lazy

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

from gestion import settings

from .forms import (
    CustomLoginForm,
    RegistroUsuarioForm,
    CustomPasswordResetForm,
    AdminEditUserForm,
    UserEditProfileForm,
)
from .models import Usuario
from .decorators import role_required

from notification.views import send_activation_email

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm

    def form_valid(self, form):
        """Si el login es correcto, controlamos la sesión."""
        remember = self.request.POST.get('remember_me')
        user = form.get_user()
        auth_login(self.request, user)

        if not remember:
            # Expira al cerrar navegador
            self.request.session.set_expiry(0)
        else:
            # Recuerda por 30 días
            self.request.session.set_expiry(60 * 60 * 24 * 30)

        if getattr(user, "must_change_password", False):
            return redirect('cambiar_contrasena_inicial')

        return redirect('/')


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if getattr(user, "must_change_password", False):
                return redirect('change_new_password')
            return redirect('/')  # manda a la pagina principal
    else:
        form = CustomLoginForm()
    return render(request, "login/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')


def es_superusuario(user):
    if not user.is_authenticated or not user.is_staff:
        raise PermissionDenied
    return True


def success_view(request):
    return render(request, "login/success.html")

@login_required
@role_required(allowed_roles=['Administrador'])
def registrar_usuario(request):
    if request.method == "POST":
        # Si viene de la pantalla de confirmación
        if "confirm" in request.POST:
            form = RegistroUsuarioForm(request.POST)
            if form.is_valid():
                user = form.save()  # aquí NO se genera clave, queda inactivo

                try:
                    send_activation_email(request, user)
                    messages.success(
                        request,
                        f"Usuario creado correctamente. Se envió un correo de activación a {user.correo}."
                    )
                    return render(request, "login/success.html")
                except Exception as e:
                    print("⚠️ ERROR EN ENVÍO DE CORREO:", e)
                    messages.error(request, f"No se pudo enviar el correo: {e}")
                    return redirect("registrar_usuario")

            # Si el form no es válido, volver al formulario normal
            return render(
                request,
                "login/registrar.html",
                {
                    "form": form,
                    "title": "Registrar Nuevo Usuario",
                    "submit_text": "Registrar",
                    "cancel_url": "/",
                }
            )

        # Primer POST (desde formulario de registro)
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            rol = form.cleaned_data["roles"]
            casetas = form.cleaned_data["ware_assig"]
            return render(
                request,
                "login/confirm_registro.html",
                {
                    "form": form,
                    "title": "Confirmar datos del nuevo usuario",
                    "role_name": rol.name_role,
                    "casetas": casetas,
                }
            )

    else:
        form = RegistroUsuarioForm()

    return render(
        request,
        "login/registrar.html",
        {
            "form": form,
            "title": "Registrar Nuevo Usuario",
            "submit_text": "Registrar",
            "cancel_url": "/",
        }
    )
# -------- Password Reset (usa tu form y tus templates) --------
class CustomPasswordResetView(PasswordResetView):
    template_name = "login/password_reset_form.html"
    subject_template_name = "login/password_reset_subject.txt"
    html_email_template_name = "login/password_reset_email.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')


@login_required
def change_new_password(request):
    user = request.user
    if not getattr(user, "must_change_password", False):
        return redirect('/')  # si no debe cambiarla, lo mandamos al home

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.must_change_password = False
            user.save()
            update_session_auth_hash(request, user)  # mantiene la sesión activa
            messages.success(request, "Tu contraseña fue actualizada correctamente.")
            return redirect('/')
    else:
        form = SetPasswordForm(user)
    return render(request, 'login/change_new_password.html', {'form': form})


# ======================================================
#   NUEVAS VISTAS: GESTIÓN DE USUARIOS Y MI PERFIL
# ======================================================

@login_required
@role_required(allowed_roles=['Administrador'])
def admin_edit_user(request, user_id):
    """
    Vista para que el ADMIN edite roles y casetas asignadas de un usuario.
    """
    usuario = get_object_or_404(Usuario, pk=user_id)

    if request.method == 'POST':
        form = AdminEditUserForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('user_list')  # listado de usuarios
    else:
        form = AdminEditUserForm(instance=usuario)

    return render(request, 'login/admin_edit_user.html', {
        'form': form,
        'usuario': usuario,
        'title': "Editar Usuario (Admin)",
        'submit_text': "Guardar Cambios",
        'cancel_url': "/",  # ajusta si quieres volver a otra ruta
    })


@login_required
def user_edit_profile(request):
    """
    Vista para que el propio usuario edite su perfil (correo y teléfono).
    """
    user = request.user  # instancia de Usuario

    if request.method == 'POST':
        form = UserEditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('dashboard:home')  # ajusta al nombre de tu home en dashboard
    else:
        form = UserEditProfileForm(instance=user)

    return render(request, 'login/user_edit_profile.html', {
        'form': form,
        'usuario': user,
        'title': "Mi Perfil",
        'submit_text': "Guardar Cambios",
        "cancel_url": reverse_lazy('dashboard:home')  # o donde quieras
    })


@login_required
@role_required(allowed_roles=['Administrador'])
def user_list(request):
    """
    Lista de usuarios para que el ADMIN gestione roles/casetas y activación.
    """
    usuarios = Usuario.objects.all()

    return render(request, "login/user_list.html", {
        "usuarios": usuarios,
        "title": "Lista de Usuarios"
    })


@login_required
@role_required(allowed_roles=['Administrador'])
def deactivate_user(request, user_id):
    """
    Desactiva un usuario (no puede iniciar sesión). Evita hacerlo con administradores.
    """
    usuario = get_object_or_404(Usuario, pk=user_id)

    # Evitar desactivar administradores (seguridad extra)
    if hasattr(usuario, "has_role") and usuario.has_role("Administrador"):
        messages.error(request, "No puedes desactivar un Administrador.")
        return redirect("user_list")

    usuario.is_active = False
    usuario.save()

    messages.success(request, f"El usuario {usuario.nombre_usuario} ha sido desactivado.")
    return redirect("user_list")


@login_required
@role_required(allowed_roles=['Administrador'])
def activate_user(request, user_id):
    """
    Activa un usuario previamente desactivado. También protege administradores.
    """
    usuario = get_object_or_404(Usuario, pk=user_id)

    if hasattr(usuario, "has_role") and usuario.has_role("Administrador"):
        messages.error(request, "No puedes activar un Administrador.")
        return redirect("user_list")

    usuario.is_active = True
    usuario.save()

    messages.success(request, f"El usuario {usuario.nombre_usuario} ha sido activado.")
    return redirect("user_list")

User = get_user_model()

def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace de activación no es válido o ha expirado.")
        return redirect("login")

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()           # guarda la contraseña
            user.is_active = True
            # Por si acaso quieres limpiar flags:
            # user.must_change_password = False
            user.save()

            # Opcional: loguearlo al tiro
            auth_login(
                request,
                user,
                backend=settings.AUTHENTICATION_BACKENDS[0]
            )

            messages.success(request, "Tu cuenta ha sido activada y tu contraseña fue definida correctamente.")
            return redirect("/")
    else:
        form = SetPasswordForm(user)

    return render(request, "login/change_new_password.html", {"form": form})