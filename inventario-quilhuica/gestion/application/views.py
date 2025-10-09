from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import ApplicationForm, ApplicationDetailFormSet
from .models import Application

def app_index(request):
    return render(request, 'application/application.html')


def create_application(request):
    if request.method == 'POST':
        # Instanciamos el formulario principal y el formset con los datos del POST
        form = ApplicationForm(request.POST)
        formset = ApplicationDetailFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Guardamos el formulario principal, pero sin enviarlo a la BD aún
            application = form.save(commit=False)
            # Asignamos el usuario que está realizando la aplicación
            application.applied_by = request.user
            application.save() # Ahora sí, guardamos la aplicación en la BD

            # Vinculamos el formset con la instancia de la aplicación recién creada
            formset.instance = application
            formset.save() # Guardamos todos los detalles de productos

            return redirect(reverse_lazy('alguna_url_de_exito')) # Redirige a una página de éxito

    else:
        # Si es una petición GET, mostramos los formularios vacíos
        form = ApplicationForm()
        formset = ApplicationDetailFormSet()

    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'application/create_application.html', context)