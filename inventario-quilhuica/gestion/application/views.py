from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from .forms import ApplicationForm, ApplicationDetailFormSet
from warehouse.models import Inventory, Warehouse, Equipment
from product.models import Product
from application.models import Application, ApplicationDetail


def create_application(request):
    user = request.user

    if not user.is_staff and not user.ware_assig.exists():
        messages.error(request, "No tienes una caseta asignada. Contacta al administrador.")
        return redirect('/')
    
    error_message = None  

    if request.method == 'POST':
        form = ApplicationForm(request.POST, user=user)

        if form.is_valid():
            selected_warehouse = form.cleaned_data.get('ware')

            app_instance = form.save(commit=False)
            app_instance.applied_by = user
            app_instance.ware = selected_warehouse

            formset = ApplicationDetailFormSet(request.POST, instance=app_instance, prefix='details')
            # Filtrar productos según la caseta
            for f in formset.forms:
                f.fields['product'].queryset = Product.objects.filter(
                    product_id__in=Inventory.objects.filter(warehouse=selected_warehouse).values_list('product_id', flat=True)
                )

            if formset.is_valid():
                valid_forms = [
                    f for f in formset.forms
                    if f.cleaned_data
                    and not f.cleaned_data.get('DELETE', False)
                    and f.cleaned_data.get('product')
                    and f.cleaned_data.get('quantity_packages')
                ]

                if not valid_forms:
                    error_message = " Debes agregar al menos un producto antes de continuar."
                    return render(request, 'application/application_form.html', {
                        'form': form,
                        'formset': formset,
                        'error_message': error_message,
                    })

                # Datos para la sesión
                products_data = []
                for f in valid_forms:
                    product = f.cleaned_data['product']
                    quantity = f.cleaned_data['quantity_packages']
                    inv = Inventory.objects.get(product=product, warehouse=selected_warehouse)

                    products_data.append({
                        'product_id': product.product_id,
                        'product_name': product.name_prod,
                        'presentation': f"{product.presentation.package_type} {product.presentation.content_value} {product.presentation.content_unit}",
                        'quantity': int(quantity),
                        'stock_available': int(inv.quantity_packages),
                        'stock_after': int(inv.quantity_packages - quantity)
                    })

                    sector = form.cleaned_data.get('sector')
                    sector = form.cleaned_data.get('sector')
                    request.session['pending_application'] = {
                        'warehouse_id': selected_warehouse.id,
                        'warehouse_name': selected_warehouse.name_ware,
                        'sector_id': sector.id if sector else None,
                        'equipment_id': sector.equipment.id if sector else None,
                        'sector_name': (
                            f"{sector.equipment.nombre_equipo} — Sector {sector.sector_num}"
                            if sector else "No seleccionado"
                        ),
                        'products': products_data,
                    }
                return redirect('application:confirm_application')
            else:
                print("FORMSET ERRORS:", formset.errors)
                messages.error(request, "Corrige los errores del formulario de productos.")
        else:
            messages.error(request, "Corrige los errores en el formulario principal.")
            formset = ApplicationDetailFormSet(request.POST, prefix='details')

    else:
        form = ApplicationForm(user=user)
        formset = ApplicationDetailFormSet(form_kwargs={'warehouse': None}, prefix='details')

    return render(request, 'application/application_form.html', {
        'form': form,
        'formset': formset,
        'error_message': error_message,
    })


def confirm_application(request):
    pending_data = request.session.get('pending_application')
    if not pending_data:
        messages.warning(request, "No hay ninguna aplicación pendiente de confirmar.")
        return redirect('application:create_application')

    if request.method == 'POST':
        return save_application(request)

    return render(request, 'application/application_confirm.html', {
        'warehouse_name': pending_data['warehouse_name'],
        'sector_name': pending_data.get('sector_name', 'No seleccionado'),
        'products': pending_data['products'],
    })


@transaction.atomic
def save_application(request):
    pending_data = request.session.get('pending_application')
    if not pending_data:
        messages.error(request, "Sesión expirada. Por favor, crea la aplicación nuevamente.")
        return redirect('application:create_application')

    try:
        user = request.user
        warehouse = Warehouse.objects.get(id=pending_data['warehouse_id'])

        sector_id = pending_data.get('sector_id')
        equipment_id = pending_data.get('equipment_id')

        application = Application.objects.create(
            ware=warehouse,
            applied_by=user,
            sector_id=sector_id,
            equipment_id=equipment_id
        )

        for product_data in pending_data['products']:
            product = Product.objects.get(product_id=product_data['product_id'])
            quantity = product_data['quantity']

            ApplicationDetail.objects.create(
                application=application,
                product=product,
                quantity_packages=quantity
            )

            inv = Inventory.objects.get(product=product, warehouse=warehouse)
            if inv.quantity_packages < quantity:
                raise ValueError(f"Stock insuficiente para {product.name_prod}")

            inv.quantity_packages -= quantity
            inv.save()

        del request.session['pending_application']
        messages.success(request, f" Aplicación #{application.id} creada exitosamente y stock actualizado.")
        return redirect('application:create_application')

    except Exception as e:
        messages.error(request, f" Error al guardar la aplicación: {str(e)}")
        return redirect('application:confirm_application')


def cancel_application(request):
    if 'pending_application' in request.session:
        del request.session['pending_application']
        messages.info(request, "Aplicación cancelada.")
    return redirect('application:create_application')


def get_products_by_warehouse(request):
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


def get_sectores_by_caseta(request):
    caseta_id = request.GET.get("caseta_id")
    if not caseta_id:
        return JsonResponse([], safe=False)

    equipos = Equipment.objects.filter(caseta_id=caseta_id).prefetch_related("sectores")

    data = []
    for equipo in equipos:
        data.append({
            "equipo": equipo.nombre_equipo,  
            "sectores": [
                {"id": s.id, "nombre": f"Sector {s.sector_num}"} for s in equipo.sectores.all()
            ],
        })
    return JsonResponse(data, safe=False)