# warehouse/tests.py
from datetime import datetime, timedelta, timezone
from django.test import TestCase, Client
from django.urls import reverse

from warehouse.models import Warehouse, Equipment, Sector, Inventory, Movement
from product.models import Product, Presentation, Category
from login.models import Role, Usuario


class WarehouseTests(TestCase):
    """
    Pruebas funcionales del módulo Warehouse (Casetas, Inventario y Movimientos)
    Ejecutar con: python manage.py test warehouse --verbosity 2
    """

    @classmethod
    def setUpTestData(cls):
        print("\n============================================")
        print("INICIALIZANDO DATOS DE PRUEBA - MÓDULO WAREHOUSE")
        print("============================================")

        # Roles
        cls.role_admin = Role.objects.create(name_role="Administrador")
        cls.role_supervisor = Role.objects.create(name_role="Supervisor")
        cls.role_encargado = Role.objects.create(name_role="Encargado de Caseta")

        # Usuarios
        cls.admin = Usuario.objects.create_user(
            nombre_usuario="admin", correo="admin@test.com", password="1234", is_staff=True
        )
        cls.admin.roles.add(cls.role_admin)

        cls.supervisor = Usuario.objects.create_user(
            nombre_usuario="super", correo="super@test.com", password="1234"
        )
        cls.supervisor.roles.add(cls.role_supervisor)

        cls.encargado = Usuario.objects.create_user(
            nombre_usuario="enc", correo="enc@test.com", password="1234"
        )
        cls.encargado.roles.add(cls.role_encargado)

        # Categoría y presentación base
        cls.category = Category.objects.create(name_cat="Fertilizantes", description_cat="Productos agrícolas")
        cls.presentation = Presentation.objects.create(
            package_type="saco",
            content_value=25,
            content_unit="kg",
        )

        # Producto activo
        cls.product = Product.objects_all.create(
            name_prod="Urea",
            category=cls.category,
            presentation=cls.presentation,
            expire_at=datetime.now(timezone.utc) + timedelta(days=180),
            is_active=True,
        )

        # Bodegas
        cls.main = Warehouse.objects.create(name_ware="Bodega Principal", type="main")
        cls.shed = Warehouse.objects.create(name_ware="Caseta Norte", type="shed")
        cls.encargado.ware_assig.add(cls.shed)

        # Inventarios iniciales
        cls.inv_main = Inventory.objects.create(
            product=cls.product,
            presentation=cls.presentation,
            warehouse=cls.main,
            quantity_packages=10,
        )
        cls.inv_shed = Inventory.objects.create(
            product=cls.product,
            presentation=cls.presentation,
            warehouse=cls.shed,
            quantity_packages=0,
        )

        print("✅ Datos base cargados correctamente.\n")

    def setUp(self):
        self.client = Client()

    # ==========================================================
    # TC-WARE-01: CÁLCULO DE TOTAL_CONTENT EN INVENTARIO
    # ==========================================================
    def test_inventory_total_content(self):
        print("\nTC-WARE-01: CÁLCULO DE TOTAL_CONTENT EN INVENTARIO")
        print("--------------------------------------------")
        self.inv_main.quantity_packages = 12
        self.inv_main.save()
        esperado = 12 * self.inv_main.presentation.content_value
        print(f"Paso 1: Recalcular total_content → {esperado}")
        print(f"Resultado: {self.inv_main.total_content}")
        if self.inv_main.total_content == esperado:
            print("ESTADO: OK\nDETALLE: Total content calculado correctamente.")
        else:
            print("ESTADO: ERROR\nDETALLE: Cálculo incorrecto.")
        self.assertEqual(self.inv_main.total_content, esperado)

    # ==========================================================
    # TC-WARE-02: RESTRICCIÓN DE UNICIDAD EN EQUIPO Y SECTOR
    # ==========================================================
    def test_unique_equipment_and_sector(self):
        print("\nTC-WARE-02: VALIDAR RESTRICCIÓN DE UNICIDAD EN EQUIPO Y SECTOR")
        print("--------------------------------------------")
        eq = Equipment.objects.create(caseta=self.shed, nombre_equipo="A Citrícos")
        Sector.objects.create(equipment=eq, sector_num=1)
        with self.assertRaises(Exception):
            Sector.objects.create(equipment=eq, sector_num=1)
        with self.assertRaises(Exception):
            Equipment.objects.create(caseta=self.shed, nombre_equipo="A Citrícos")
        print("ESTADO: OK\nDETALLE: Restricciones de unicidad validadas correctamente.")

    # ==========================================================
    # TC-WARE-03: CREACIÓN DE CASETA POR ADMINISTRADOR
    # ==========================================================
    def test_create_caseta_view(self):
        print("\nTC-WARE-03: CREACIÓN DE CASETA POR ADMINISTRADOR")
        print("--------------------------------------------")
        self.client.force_login(self.admin)
        url = reverse("warehouse:caseta_create")
        data = {
            "name_ware": "Caseta Nueva",
            "description": "Caseta de prueba",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nombre_equipo": "Equipo 1",
            "form-0-sectores_count": "2",
        }
        response = self.client.post(url, data)
        print(f"Paso 1: Redirección correcta (código {response.status_code})")
        creada = Warehouse.objects.filter(name_ware="Caseta Nueva").exists()
        print(f"Paso 2: Caseta creada → {creada}")
        if creada:
            print("ESTADO: OK\nDETALLE: Caseta registrada correctamente.")
        else:
            print("ESTADO: ERROR\nDETALLE: Caseta no creada.")
        self.assertTrue(creada)

    # ==========================================================
    # TC-WARE-04: EDICIÓN DE CASETA EXISTENTE
    # ==========================================================
    def test_edit_caseta_view(self):
        print("\nTC-WARE-04: EDICIÓN DE CASETA EXISTENTE")
        print("--------------------------------------------")
        self.client.force_login(self.supervisor)
        url = reverse("warehouse:caseta_edit", args=[self.shed.id])
        data = {
            "name_ware": "Caseta Actualizada",
            "description": "Modificada",
            "form-TOTAL_FORMS": "0",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(url, data)
        self.shed.refresh_from_db()
        print(f"Paso 1: Redirección {response.status_code}")
        print(f"Paso 2: Nombre actual → {self.shed.name_ware}")
        print("ESTADO: OK\nDETALLE: Caseta editada correctamente.")
        self.assertIn("Actualizada", self.shed.name_ware)

    # ==========================================================
    # TC-WARE-05: ELIMINACIÓN DE CASETA POR ADMINISTRADOR
    # ==========================================================
    def test_delete_caseta_view(self):
        print("\nTC-WARE-05: ELIMINACIÓN DE CASETA POR ADMINISTRADOR")
        print("--------------------------------------------")
        self.client.force_login(self.admin)
        # eliminar inventarios asociados para permitir borrado
        Inventory.objects.filter(warehouse=self.shed).delete()
        url = reverse("warehouse:caseta_delete", args=[self.shed.id])
        response = self.client.post(url)
        existe = Warehouse.objects.filter(pk=self.shed.id).exists()
        print(f"Paso 1: Código respuesta → {response.status_code}")
        print(f"Paso 2: Caseta aún existe → {existe}")
        if not existe:
            print("ESTADO: OK\nDETALLE: Caseta eliminada correctamente.")
        else:
            print("ESTADO: ERROR\nDETALLE: Caseta no se eliminó.")
        self.assertFalse(existe)

    # ==========================================================
    # TC-WARE-06: ACCESO RESTRINGIDO SEGÚN ROL
    # ==========================================================
    def test_permission_restriction(self):
        print("\nTC-WARE-06: ACCESO RESTRINGIDO SEGÚN ROL")
        print("--------------------------------------------")
        self.client.force_login(self.encargado)
        url = reverse("warehouse:caseta_create")
        response = self.client.get(url)
        print(f"Paso 1: Código respuesta → {response.status_code}")
        if response.status_code in [302, 403]:
            print("ESTADO: OK\nDETALLE: Usuario sin permisos bloqueado correctamente.")
        else:
            print("ESTADO: ERROR\nDETALLE: Se permitió acceso indebido.")
        self.assertIn(response.status_code, [302, 403])

    # ==========================================================
    # TC-WARE-07: TRASLADO DE PRODUCTO ENTRE BODEGAS
    # ==========================================================
    def test_transfer_product(self):
        print("\nTC-WARE-07: TRASLADO DE PRODUCTO ENTRE BODEGAS")
        print("--------------------------------------------")
        self.client.force_login(self.supervisor)

        # asegurar que exista bodega principal visible
        Warehouse.objects.get_or_create(
            type="main",
            defaults={"name_ware": "Bodega Principal", "description": "Creada para test"}
        )

        url = reverse("warehouse:transfer_product")
        data = {
            "ware_origin": self.main.id,
            "ware_destin": self.shed.id,
            "description": "Traslado de prueba",
            "form-0-product": self.product.product_id,
            "form-0-quantity": 3,
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(url, data)
        self.inv_main.refresh_from_db()
        self.inv_shed.refresh_from_db()

        print(f"Paso 1: Código respuesta → {response.status_code}")
        print(f"Paso 2: Stock actualizado\n    Bodega Principal → {self.inv_main.quantity_packages}\n    Caseta → {self.inv_shed.quantity_packages}")

        if self.inv_main.quantity_packages == 7 and self.inv_shed.quantity_packages == 3:
            print("ESTADO: OK\nDETALLE: Traslado realizado correctamente.")
        else:
            print("ESTADO: ERROR\nDETALLE: Stock inconsistente tras traslado.")

        self.assertEqual(self.inv_main.quantity_packages, 7)
        self.assertEqual(self.inv_shed.quantity_packages, 3)
