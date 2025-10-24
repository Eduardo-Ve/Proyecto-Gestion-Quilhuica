from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import (
    logout, 
    login as auth_login, 
    update_session_auth_hash
)
from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import SetPasswordForm
from .forms import CustomLoginForm, RegistroUsuarioForm, CustomPasswordResetForm
from notification.views import send_welcome_email

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
        if user.must_change_password:
            return redirect('cambiar_contrasena_inicial')
        return redirect('/')


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.must_change_password:
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



@user_passes_test(es_superusuario)
def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            temp_password = getattr(user, "_temp_password", None)

            # Enviar correo de bienvenida
            send_welcome_email(user, temp_password)

            messages.success(request, f"Usuario creado correctamente. Se envió un correo a {user.correo}.")
            return render(request, "login/success.html", {"temp_password": temp_password})
    else:
        form = RegistroUsuarioForm()
    return render(request, 'login/registrar.html', {"form": form})

#-------- Password Reset (usa tu form y tus templates) --------
class CustomPasswordResetView(PasswordResetView):
    template_name = "login/password_reset_form.html"
    subject_template_name = "login/password_reset_subject.txt"
    html_email_template_name = "login/password_reset_email.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')


@login_required
def change_new_password(request):
    user = request.user
    if not user.must_change_password:
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