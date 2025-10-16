from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from .forms import CustomLoginForm, RegistroUsuarioForm, CustomPasswordResetForm


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    # el template lo pasas en urls.py via as_view(template_name='login/login.html')


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('/')  # manda a home/core (ajústalo si usas otro nombre de ruta)
    else:
        form = CustomLoginForm()
    return render(request, "login/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')  # sin namespace, tal como elegiste


def es_superusuario(user):
    if not user.is_authenticated or not user.is_superuser:
        raise PermissionDenied
    return True


def success_view(request):
    return render(request, "registro/success.html")


@user_passes_test(es_superusuario)
def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            telefono = form.cleaned_data["telefono"]
            return render(request, "registro/success.html", {"telefono": telefono})
    else:
        form = RegistroUsuarioForm()
    return render(request, 'login/registrar.html', {"form": form})


# -------- Password Reset (usa tu form y tus templates) --------
class CustomPasswordResetView(PasswordResetView):
    template_name = "login/password_reset_form.html"
    subject_template_name = "login/password_reset_subject.txt"
    html_email_template_name = "login/password_reset_email.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
