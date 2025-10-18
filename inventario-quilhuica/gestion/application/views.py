from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .forms import ApplicationForm, ApplicationDetailFormSet
from warehouse.models import Inventory, Warehouse
from product.models import Product

# El decorador asegura que todas las operaciones de la base de datos
# (crear aplicación, crear detalles, descontar stock) ocurran como una sola transacción.
# Si algo falla, todo se revierte.
@transaction.atomic
def create_application(request):
    products = Product.objects.select_related('presentation').all()

    if request.method == 'POST':
        # 1. Instanciar el formulario principal con los datos del POST
        form = ApplicationForm(request.POST)

        # 2. Validar el formulario principal (para asegurarnos de que se seleccionó una bodega)
        if form.is_valid():
            # Creamos una instancia de Application en memoria (sin guardarla aún)
            # para poder pasársela al formset.
            application_instance = form.save(commit=False)
            
            # 3. Instanciar el formset, vinculándolo a la instancia de la aplicación.
            # Esto es CRUCIAL para que nuestro `clean()` en forms.py pueda acceder a la bodega.
            formset = ApplicationDetailFormSet(request.POST, instance=application_instance)

            # 4. Validar el formset. Aquí se ejecuta nuestra lógica de stock en forms.py.
            if formset.is_valid():
                # ya si pasa de aqui es pq va bien xd, mejorar igual la interfaz                
                # Asignamos el usuario y guardamos la aplicación principal en la Base de datos 
                application_instance.applied_by = request.user
                application_instance.save()
                
                # Guardamos los detalles del formset (que ya están vinculados a la aplicación)
                details = formset.save()

                # 5. Descontar el stock. Esta lógica ahora es segura porque ya validamos todo.
                for detail in details:
                    # Usamos un bloque try/except por si acaso, aunque no debería fallar pero igual va.
                    try:
                        inventory = Inventory.objects.get(
                            product=detail.product,
                            warehouse=application_instance.ware
                        )
                        inventory.quantity_packages -= detail.quantity_packages
                        inventory.save()
                    except Inventory.DoesNotExist:
                        # Este caso es improbable si la validación del formset funcionó,
                        # ya aqui mandamos como buena practica que te diga si no encontro el inventario 
                        messages.error(request, f"Error crítico: No se encontró el inventario para {detail.product} al momento de actualizar.")
                        # La transacción se revertirá automáticamente al salir con error.
                        return redirect('application:create_application')


                messages.success(request, "Aplicación registrada y stock actualizado correctamente.")
                return redirect('application:create_application')
        else:
            # Si el form principal no es válido (ej. no se eligió bodega),
            # instanciamos el formset con los datos del POST para que el usuario no pierda lo que escribió.
            formset = ApplicationDetailFormSet(request.POST)
        
        # Si llegamos aquí es porque 'form' o 'formset' no fueron válidos.
        # Mostramos un mensaje de error general. Los errores específicos de cada campo
        # se mostrarán automáticamente en el template.
        messages.error(request, "Por favor, corrige los errores en el formulario.")

    else: # request.method == 'GET'
        # Si es la primera vez que se carga la página, creamos formularios vacíos.
        form = ApplicationForm()
        formset = ApplicationDetailFormSet()

    # Este return se ejecuta para las peticiones GET y para las POST que fallaron la validación.
    return render(request, 'application/application_form.html', {
        'form': form,
        'formset': formset,
        'products': products,
    })