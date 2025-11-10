from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone

from login.models import Usuario, Role
from warehouse.models import Warehouse, Equipment, Sector, Inventory
from product.models import Category, Presentation, Product
from application.models import Application, ApplicationDetail


class ApplicationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("\n============================================")
        print("INICIALIZANDO DATOS DE PRUEBA - MÓDULO APPLICATION")
        print("============================================")

        # 1️⃣ Crear primero la bodega principal
        cls.bodega_principal = Warehouse.objects.create(
            name_ware="Bodega Principal",
            type="main",
            description="Bodega central de referencia para pruebas"
        )

        # 2️⃣ Roles y usuario
        cls.role_encargado = Role.objects.create(name_role="Encargado de Caseta")
        cls.user = Usuario.objects.create_user(
            nombre_usuario="encargado",
            correo="encargado@test.com",
            password="enc123",
        )
        cls.user.roles.add(cls.role_encargado)

        # 3️⃣ Caseta, equipo, sector
        cls.caseta = Warehouse.objects.create(name_ware="Caseta A", type="shed")
        cls.equipo = Equipment.objects.create(caseta=cls.caseta, nombre_equipo="Equipo 1")
        cls.sector = Sector.objects.create(equipment=cls.equipo, sector_num=1)
        cls.user.ware_assig.add(cls.caseta)

        # 4️⃣ Categoría, presentación y producto (dispara señal al crear producto)
        cls.categoria = Category.objects.create(name_cat="Fertilizantes")
        cls.presentacion = Presentation.objects.create(
            package_type="saco", content_value=25, content_unit="kg"
        )
        cls.producto = Product.objects_all.create(
            name_prod="Urea",
            category=cls.categoria,
            presentation=cls.presentacion,
            expire_at=timezone.now() + timezone.timedelta(days=180),
            is_active=True,
        )

        # 5️⃣ Inventarios adicionales (Caseta + Bodega principal para testeo)
        cls.inventario_caseta = Inventory.objects.create(
            product=cls.producto,
            presentation=cls.presentacion,
            warehouse=cls.caseta,
            quantity_packages=10,
        )

        cls.inventario_principal = Inventory.objects.filter(
            product=cls.producto,
            warehouse=cls.bodega_principal
        ).first()

        if cls.inventario_principal:
            cls.inventario_principal.quantity_packages = 50
            cls.inventario_principal.save()
            print("Inventario existente en Bodega Principal actualizado a 50 unidades.")
        else:
            cls.inventario_principal = Inventory.objects.create(
                product=cls.producto,
                presentation=cls.presentacion,
                warehouse=cls.bodega_principal,
                quantity_packages=50,
            )
            print("Inventario creado manualmente para Bodega Principal.")

        print("Datos base cargados correctamente.\n")

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def _log(self, title, status="OK", detail=None):
        """Formato uniforme para salida de texto en los tests."""
        print("--------------------------------------------")
        print(f"{title}")
        print(f"ESTADO: {status}")
        if detail:
            print(f"DETALLE: {detail}")
        print("--------------------------------------------\n")

    # -------------------------------------------------------
    # TC-APP-01 — Crear aplicación
    # -------------------------------------------------------
    def test_01_crear_aplicacion_producto(self):
        print("TC-APP-01: CREACIÓN DE APLICACIÓN DE PRODUCTO")
        create_url = reverse("application:create_application")
        confirm_url = reverse("application:confirm_application")

        data = {
            "ware": self.caseta.id,
            "sector": self.sector.id,
            "details-TOTAL_FORMS": "1",
            "details-INITIAL_FORMS": "0",
            "details-0-product": self.producto.product_id,
            "details-0-quantity_packages": "2",
        }

        # Paso 1: creación
        response = self.client.post(create_url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn(confirm_url, response["Location"])
        self._log("Paso 1: Redirección correcta hacia confirmación", "OK")

        # Paso 2: confirmar aplicación
        session = self.client.session
        session["pending_application"] = {
            "warehouse_id": self.caseta.id,
            "warehouse_name": self.caseta.name_ware,
            "sector_id": self.sector.id,
            "equipment_id": self.equipo.id,
            "sector_name": f"{self.equipo.nombre_equipo} — Sector {self.sector.sector_num}",
            "products": [
                {
                    "product_id": self.producto.product_id,
                    "product_name": self.producto.name_prod,
                    "presentation": f"{self.presentacion.package_type} {self.presentacion.content_value} {self.presentacion.content_unit}",
                    "quantity": 2,
                    "stock_available": int(self.inventario_caseta.quantity_packages),
                    "stock_after": int(self.inventario_caseta.quantity_packages - 2),
                }
            ],
        }
        session.save()

        response2 = self.client.post(confirm_url, follow=True)
        self.assertEqual(response2.status_code, 200)

        apps = Application.objects.count()
        details = ApplicationDetail.objects.count()

        # Refrescar inventario y verificar descuento
        self.inventario_caseta.refresh_from_db()
        stock = self.inventario_caseta.quantity_packages

        self.assertEqual(apps, 1)
        self.assertEqual(details, 1)
        self.assertEqual(stock, 8)

        self._log(
            "Paso 2: Aplicación creada y stock actualizado",
            "OK",
            f"Aplicaciones={apps}, Detalles={details}, StockRestante={stock}",
        )

    # -------------------------------------------------------
    # TC-APP-02 — Validación sector vs caseta
    # -------------------------------------------------------
    def test_02_validar_sector_vs_caseta(self):
        print("TC-APP-02: VALIDAR RELACIÓN SECTOR ↔ CASETA")
        otra_caseta = Warehouse.objects.create(name_ware="Caseta B", type="shed")

        data = {
            "ware": otra_caseta.id,
            "sector": self.sector.id,
            "details-TOTAL_FORMS": "1",
            "details-INITIAL_FORMS": "0",
            "details-0-product": self.producto.product_id,
            "details-0-quantity_packages": "1",
        }

        resp = self.client.post(reverse("application:create_application"), data, follow=True)
        msgs = [str(m) for m in get_messages(resp.wsgi_request)]

        self.assertEqual(Application.objects.count(), 0)
        self.assertTrue(any("corrige" in m.lower() for m in msgs))
        self._log(
            "Validación de sector ajeno a caseta",
            "OK",
            f"Mensajes={msgs}",
        )

    # -------------------------------------------------------
    # TC-APP-03 — Cancelar aplicación
    # -------------------------------------------------------
    def test_03_cancelar_aplicacion(self):
        print("TC-APP-03: CANCELAR APLICACIÓN PENDIENTE")
        session = self.client.session
        session["pending_application"] = {"warehouse_id": self.caseta.id}
        session.save()

        resp = self.client.get(reverse("application:cancel_application"), follow=True)
        msgs = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any("cancelada" in m.lower() for m in msgs))
        self._log("Cancelación de aplicación", "OK", f"Mensajes={msgs}")

    # -------------------------------------------------------
    # TC-APP-04 — Campos obligatorios
    # -------------------------------------------------------
    def test_04_validar_campos_obligatorios(self):
        print("TC-APP-04: VALIDAR CAMPOS OBLIGATORIOS")
        data = {
            "ware": "",
            "sector": "",
            "details-TOTAL_FORMS": "1",
            "details-INITIAL_FORMS": "0",
            "details-0-product": "",
            "details-0-quantity_packages": "",
        }

        resp = self.client.post(reverse("application:create_application"), data, follow=True)
        msgs = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any("corrige" in m.lower() for m in msgs))
        self._log("Validación de campos vacíos", "OK", f"Mensajes={msgs}")

    # -------------------------------------------------------
    # TC-APP-05 — Stock insuficiente
    # -------------------------------------------------------
    def test_05_stock_insuficiente(self):
        print("TC-APP-05: VALIDAR STOCK INSUFICIENTE")
        data = {
            "ware": self.caseta.id,
            "sector": self.sector.id,
            "details-TOTAL_FORMS": "1",
            "details-INITIAL_FORMS": "0",
            "details-0-product": self.producto.product_id,
            "details-0-quantity_packages": "999",
        }

        resp = self.client.post(reverse("application:create_application"), data, follow=True)
        msgs = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any("formulario de productos" in m.lower() for m in msgs))

        formset_errors = getattr(resp.context, "formset", None)
        if formset_errors:
            print("Formset Errors:", formset_errors.errors)

        self._log(
            "Validación de stock insuficiente",
            "OK",
            f"Mensajes={msgs}",
        )


