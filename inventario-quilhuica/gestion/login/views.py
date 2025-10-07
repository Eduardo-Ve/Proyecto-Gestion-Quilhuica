from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm

# Create your views here.   


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('')  # reemplaza con tu página principal
    else:
        form = CustomLoginForm()
    return render(request, "login/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')


from .forms import RegistroUsuarioForm  # <-- aquí importamos el form correcto


def es_superusuario(user):
    if not user.is_authenticated or not user.is_superuser:
        raise PermissionDenied
    return True


def success_view(request):
    return render(request, "registro/success.html")


@user_passes_test(es_superusuario)
def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)  # <-- usamos RegistroUsuarioForm
        if form.is_valid():
            user = form.save()
            telefono = form.cleaned_data["telefono"]  # aquí ya viene en formato +56
            return render(request, "registro/success.html", {"telefono": telefono})
    else:
        form = RegistroUsuarioForm()  # <-- también aquí
    return render(request, 'login/registrar.html', {"form": form})
