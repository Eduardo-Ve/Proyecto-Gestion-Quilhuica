from django.test import TestCase, Client
from django.urls import reverse
from .models import Warehouse
from .forms import WarehouseForm, TransferForm, InventoryEntryForm
from product.models import Product, Category, Presentation

# Prueba unitaria para el modelo Warehouse
class WarehouseModelTest(TestCase):
    def test_creacion_almacen(self):
        """
        Prueba que se puede crear un almacén y que sus campos se guardan correctamente.
        """
        warehouse = Warehouse.objects.create(name_ware="Central", description="Principal", type="main")
        self.assertEqual(warehouse.name_ware, "Central")
        self.assertEqual(warehouse.type, "main")

# Prueba unitaria para el formulario WarehouseForm
class WarehouseFormTest(TestCase):
    def test_formulario_valido(self):
        """
        Prueba que el formulario WarehouseForm es válido con datos correctos.
        """
        form_data = {'name_ware': 'Caseta Norte', 'description': 'Caseta secundaria', 'type': 'shed'}
        form = WarehouseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_formulario_invalido(self):
        """
        Prueba que el formulario WarehouseForm es inválido si falta el campo 'name_ware'.
        """
        form_data = {'description': 'Sin nombre', 'type': 'shed'}
        form = WarehouseForm(data=form_data)
        self.assertFalse(form.is_valid())

# Prueba unitaria para el formulario TransferForm
class TransferFormTest(TestCase):
    def setUp(self):
        # Crear datos necesarios para el formulario
        self.cat = Category.objects.create(name_cat="Cat", description_cat="desc")
        self.prod = Product.objects.create(name_prod="Producto", category=self.cat)
        self.pres = Presentation.objects.create(product=self.prod, package_type="saco", content_value=25, content_unit="kg")
        self.main = Warehouse.objects.create(name_ware="Bodega", type="main")
        self.shed = Warehouse.objects.create(name_ware="Caseta", type="shed")

    def test_transfer_form_valido(self):
        """
        Prueba que el formulario TransferForm es válido con datos correctos.
        """
        form_data = {
            'product': self.prod.product_id,  # Usar product_id si es el PK
            'presentation': self.pres.presentation_id,  # Usar presentation_id si es el PK
            'ware_origin': self.main.id,
            'ware_destin': self.shed.id,
            'quantity': 10,
            'description': 'Traslado de prueba'
        }
        form = TransferForm(data=form_data)
        self.assertTrue(form.is_valid())

# Prueba unitaria para el formulario InventoryEntryForm
class InventoryEntryFormTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name_cat="Cat", description_cat="desc")
        self.prod = Product.objects.create(name_prod="Producto", category=self.cat)
        self.pres = Presentation.objects.create(product=self.prod, package_type="saco", content_value=25, content_unit="kg")
        self.main = Warehouse.objects.create(name_ware="Bodega", type="main")

    def test_inventory_entry_form_valido(self):
        """
        Prueba que el formulario InventoryEntryForm es válido y guarda correctamente el inventario.
        """
        form_data = {
            'warehouse': self.main.id,
            'product': self.prod.product_id,  # Usar product_id si es el PK
            'presentation': self.pres.presentation_id,  # Usar presentation_id si es el PK
            'quantity_packages': 5
        }
        form = InventoryEntryForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Solo guardar si el formulario es válido y el modelo lo permite
        if form.is_valid():
            inventory = form.save(commit=True)
            self.assertEqual(inventory.quantity_packages, 5)

from django.contrib.auth import get_user_model

class WarehouseListViewTest(TestCase):
    
    def setUp(self):
        # Crear usuario y autenticar
        self.user = get_user_model().objects.create_user(
            nombre_usuario='testuser',
            correo='testuser@example.com',
            password='testpass'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        Warehouse.objects.create(name_ware="Principal", type="main")
        Warehouse.objects.create(name_ware="mandarina", type="shed")
    def test_listado_almacenes(self):
        """
        Prueba que la vista de listado muestra los almacenes creados.
        """
        response = self.client.get(reverse('warehouse:caseta_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Principal")
        self.assertContains(response, "mandarina")

class WarehouseCreateViewTest(TestCase):
    def setUp(self):
        # Crear usuario y autenticar
        self.user = get_user_model().objects.create_user(
            nombre_usuario='testuser',
            correo='testuser@example.com',
            password='testpass'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_crear_almacen(self):
        """
        Prueba que se puede crear un almacén usando la vista de creación.
        """
        response = self.client.post(reverse('warehouse:caseta_create'), {
            'name_ware': 'Nueva Caseta',
            'description': 'Caseta de prueba',
            'type': 'shed'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Warehouse.objects.filter(name_ware='Nueva Caseta').exists())
