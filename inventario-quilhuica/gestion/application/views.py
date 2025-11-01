from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .forms import ApplicationForm, ApplicationDetailFormSet
from warehouse.models import Inventory, Warehouse
from product.models import Product
from django.http import JsonResponse

@transaction.atomic
def create_application(request):
    user = request.user
    user_warehouse = user.casetas_asignadas if not user.is_staff else None

    if not user.is_staff and not user_warehouse:
        messages.error(request, "No tienes una caseta asignada. Contacta al administrador.")
        return redirect('/')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, user=user)

        if user.is_staff:
            selected_warehouse = Warehouse.objects.filter(id=request.POST.get('ware')).first()
        else:
            selected_warehouse = user_warehouse

        if form.is_valid():
            app_instance = form.save(commit=False)
            app_instance.applied_by = user
            app_instance.ware = selected_warehouse

            formset = ApplicationDetailFormSet(request.POST, instance=app_instance, warehouse=selected_warehouse)

            # Validar formset y que haya al menos un producto válido
            if formset.is_valid():
                # Verificamos que no todos los forms estén vacíos o eliminados
                valid_forms = [
                    f for f in formset.forms
                    if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
                ]
                if not valid_forms:
                    messages.warning(request, "Debes agregar al menos un producto antes de guardar la aplicación.")
                    return render(request, 'application/application_form.html', {
                        'form': form,
                        'formset': formset,
                    })

                # Si hay productos válidos, guardamos todo
                app_instance.save()
                details = formset.save()

                for d in details:
                    inv = Inventory.objects.get(product=d.product, warehouse=selected_warehouse)
                    inv.quantity_packages -= d.quantity_packages
                    inv.save()

                messages.success(request, "Aplicación creada y stock actualizado correctamente.")
                return redirect('application:create_application')
            else:
                messages.error(request, "Corrige los errores del formulario de productos.")
        else:
            messages.error(request, "Corrige los errores en el formulario principal.")
            formset = ApplicationDetailFormSet(request.POST, warehouse=selected_warehouse)
    else:
        form = ApplicationForm(user=user)
        selected_warehouse = user_warehouse if user_warehouse else None
        formset = ApplicationDetailFormSet(warehouse=selected_warehouse)

    return render(request, 'application/application_form.html', {
        'form': form,
        'formset': formset,
    })


def get_products_by_warehouse(request):
    """
    Retorna los productos disponibles en una caseta en formato JSON.
    """
    warehouse_id = request.GET.get("warehouse_id")
    if not warehouse_id:
        return JsonResponse({"error": "No se envió un warehouse_id"}, status=400)

    inventories = Inventory.objects.filter(warehouse_id=warehouse_id).select_related('product', 'presentation')
    data = [
        {
            "id": inv.product.product_id,
            "name": inv.product.name_prod,
            "presentation": f"{inv.product.presentation.package_type} {inv.product.presentation.content_value} {inv.product.presentation.content_unit}",
            "stock": inv.quantity_packages,
        }
        for inv in inventories
    ]

    return JsonResponse({"products": data})