from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.core.exceptions import PermissionDenied

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
    return render(request, 'registro/registrar.html', {"form": form})
