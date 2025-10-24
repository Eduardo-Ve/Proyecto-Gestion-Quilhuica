from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from .forms import ApplicationForm, ApplicationDetailFormSet
from warehouse.models import Inventory, Warehouse
from django.http import JsonResponse
from product.models import *
from application.models import * 
import json


def create_application(request):
    """Vista inicial: validar formulario y redirigir a confirmación"""
    user = request.user
    user_warehouse = user.caseta_asignada if not user.is_staff else None

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
            # Crear instancia temporal (sin guardar en BD)
            app_instance = form.save(commit=False)
            app_instance.applied_by = user
            app_instance.ware = selected_warehouse

            formset = ApplicationDetailFormSet(
                request.POST,
                instance=app_instance,
                prefix='details'
            )

            # Inyectar queryset de productos
            for f in formset.forms:
                f.fields['product'].queryset = Product.objects.filter(
                    product_id__in=Inventory.objects.filter(
                        warehouse=selected_warehouse
                    ).values_list('product_id', flat=True)
                )

            if formset.is_valid():
                valid_forms = [
                    f for f in formset.forms
                    if f.cleaned_data 
                    and not f.cleaned_data.get('DELETE', False)
                    and f.cleaned_data.get('product')  # ✅ Verificar que tenga producto
                    and f.cleaned_data.get('quantity_packages')  # ✅ Verificar que tenga cantidad
                ]

                if not valid_forms:
                    messages(request, "Debes agregar al menos un producto antes de continuar.")
                    return render(request, 'application/application_form.html', {
                        'form': form,
                        'formset': formset,
                    })

                # 🔥 Guardar datos en sesión para confirmación
                products_data = []
                for f in valid_forms:
                    product = f.cleaned_data['product']
                    quantity = f.cleaned_data['quantity_packages']
                    
                    # Obtener información del inventario
                    inv = Inventory.objects.get(product=product, warehouse=selected_warehouse)
                    
                    products_data.append({
                        'product_id': product.product_id,
                        'product_name': product.name_prod,
                        'presentation': f"{product.presentation.package_type} {product.presentation.content_value} {product.presentation.content_unit}",
                        'quantity': float(quantity),
                        'stock_available': float(inv.quantity_packages),
                        'stock_after': float(inv.quantity_packages - quantity)
                    })

                request.session['pending_application'] = {
                    'warehouse_id': selected_warehouse.id,
                    'warehouse_name': selected_warehouse.name_ware,
                    'products': products_data
                }

                return redirect('application:confirm_application')
            else:
                print("FORMSET ERRORS:", formset.errors)
                messages.error(request, "Corrige los errores del formulario de productos.")
        else:
            messages.error(request, "Corrige los errores en el formulario principal.")
            formset = ApplicationDetailFormSet(
                request.POST,
                prefix='details'
            )

    else:
        form = ApplicationForm(user=user)
        formset = ApplicationDetailFormSet(form_kwargs={'warehouse': None}, prefix='details')

    return render(request, 'application/application_form.html', {
        'form': form,
        'formset': formset,
    })


def confirm_application(request):
    """Vista de confirmación: mostrar resumen antes de guardar"""
    
    # Verificar que hay datos pendientes
    pending_data = request.session.get('pending_application')
    if not pending_data:
        messages.warning(request, "No hay ninguna aplicación pendiente de confirmar.")
        return redirect('application:create_application')

    if request.method == 'POST':
        # Usuario confirmó, proceder a guardar
        return save_application(request)

    # Mostrar página de confirmación
    return render(request, 'application/application_confirm.html', {
        'warehouse_name': pending_data['warehouse_name'],
        'products': pending_data['products'],
    })


@transaction.atomic
def save_application(request):
    """Guardar definitivamente la aplicación tras confirmación"""
    
    pending_data = request.session.get('pending_application')
    if not pending_data:
        messages.error(request, "Sesión expirada. Por favor, crea la aplicación nuevamente.")
        return redirect('application:create_application')

    try:
        user = request.user
        warehouse = Warehouse.objects.get(id=pending_data['warehouse_id'])

        # Crear la aplicación
        application = Application.objects.create(
            ware=warehouse,
            applied_by=user
        )

        # Crear detalles y actualizar inventario
        for product_data in pending_data['products']:
            product = Product.objects.get(product_id=product_data['product_id'])
            quantity = product_data['quantity']

            # Crear detalle
            ApplicationDetail.objects.create(
                application=application,
                product=product,
                quantity_packages=quantity
            )

            # Actualizar inventario
            inv = Inventory.objects.get(product=product, warehouse=warehouse)
            
            # Validación final de stock (por seguridad)
            if inv.quantity_packages < quantity:
                raise ValueError(f"Stock insuficiente para {product.name_prod}")
            
            inv.quantity_packages -= quantity
            inv.save()

        # Limpiar sesión
        del request.session['pending_application']

        messages.success(request, f"✅ Aplicación #{application.id} creada exitosamente y stock actualizado.")
        return redirect('application:create_application')

    except Exception as e:
        messages.error(request, f"❌ Error al guardar la aplicación: {str(e)}")
        return redirect('application:confirm_application')


def cancel_application(request):
    """Cancelar aplicación pendiente"""
    if 'pending_application' in request.session:
        del request.session['pending_application']
        messages.info(request, "Aplicación cancelada.")
    
    return redirect('application:create_application')


# 🧩 API: productos por caseta
def get_products_by_warehouse(request):
    warehouse_id = request.GET.get("warehouse_id")
    if not warehouse_id:
        return JsonResponse({"error": "No se envió un warehouse_id"}, status=400)

    inventories = Inventory.objects.filter(
        warehouse_id=warehouse_id
    ).select_related('product', 'presentation')

    data = [
        {
            "id": inv.product.product_id,
            "name": inv.product.name_prod,
            "presentation": f"{inv.product.presentation.package_type} "
                            f"{inv.product.presentation.content_value} "
                            f"{inv.product.presentation.content_unit}",
            "stock": inv.quantity_packages,
        }
        for inv in inventories
    ]

    return JsonResponse({"products": data})