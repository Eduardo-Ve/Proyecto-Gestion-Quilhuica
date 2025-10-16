from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .forms import ApplicationForm, ApplicationDetailFormSet
from warehouse.models import Inventory
from product.models import Product

@transaction.atomic
def create_application(request):
    products = Product.objects.select_related('presentation').all()

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        formset = ApplicationDetailFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            application = form.save(commit=False)
            application.applied_by = request.user
            application.save()

            formset.instance = application
            details = formset.save()

            # Actualizar stock
            for detail in details:
                try:
                    inventory = Inventory.objects.get(
                        product=detail.product,
                        presentation=detail.product.presentation,
                        warehouse=application.ware
                    )
                    if detail.quantity_packages > inventory.quantity_packages:
                        messages.error(
                            request,
                            f"Stock insuficiente para {detail.product}. Disponible: {inventory.quantity_packages}."
                        )
                        transaction.set_rollback(True)
                        return redirect('application:create_application')

                    inventory.quantity_packages -= detail.quantity_packages
                    inventory.save()
                except Inventory.DoesNotExist:
                    messages.error(
                        request,
                        f"No existe inventario para {detail.product} en {application.ware}."
                    )
                    transaction.set_rollback(True)
                    return redirect('application:create_application')

            messages.success(request, "Aplicación registrada y stock actualizado correctamente.")
            return redirect('application:create_application')

        else:
            messages.error(request, "Revisa los errores en el formulario.")
    else:
        form = ApplicationForm()
        formset = ApplicationDetailFormSet()

    return render(request, 'application/application_form.html', {
        'form': form,
        'formset': formset,
        'products': products,
    })
