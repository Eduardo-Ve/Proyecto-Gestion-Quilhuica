from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model

from notification.models import Notification
from notification.services import create_notifications
from warehouse.models import Inventory, Warehouse
from product.models import Product, Presentation, Category

User = get_user_model()


class NotificationTests(TestCase):
    """Casos de Prueba Funcionales — Módulo Notification"""

    @classmethod
    def setUpTestData(cls):
        print("\n============================================")
        print("INICIALIZANDO DATOS DE PRUEBA - MÓDULO NOTIFICATION")
        print("============================================")

        # 1️⃣ Bodega principal
        cls.warehouse = Warehouse.objects.create(
            name_ware="Bodega Principal",
            type="main",
            description="Bodega central de referencia para notificaciones"
        )

        # 2️⃣ Usuario administrador (is_staff)
        cls.admin = User.objects.create_user(
            nombre_usuario="AdminTest",
            correo="admin@quilhuica.cl",
            telefono="999999999",
            password="1234",
            is_staff=True
        )

        # 3️⃣ Categoría y presentación
        cls.category = Category.objects.create(name_cat="Fertilizantes")
        cls.presentation = Presentation.objects.create(
            package_type="Saco",
            content_value=25,
            content_unit="kg"
        )

        # 4️⃣ Productos
        cls.product_low = Product.objects.create(
            name_prod="Urea",
            presentation=cls.presentation,
            category=cls.category,
            expire_at=timezone.now().date() + timedelta(days=90)
        )

        cls.product_expiring = Product.objects.create(
            name_prod="Nitrato Potasio",
            presentation=cls.presentation,
            category=cls.category,
            expire_at=timezone.now().date() + timedelta(days=15)
        )

        # 5️⃣ Inventarios (evitar duplicados)
        cls.inventory_low, created1 = Inventory.objects.get_or_create(
            warehouse=cls.warehouse,
            product=cls.product_low,
            presentation=cls.presentation,
            defaults={"quantity_packages": 2, "total_content": 50.0}
        )
        if not created1:
            cls.inventory_low.quantity_packages = 2
            cls.inventory_low.total_content = 50.0
            cls.inventory_low.save()
        print(f" Inventario preparado para '{cls.product_low.name_prod}' en bodega principal.")

        cls.inventory_ok, created2 = Inventory.objects.get_or_create(
            warehouse=cls.warehouse,
            product=cls.product_expiring,
            presentation=cls.presentation,
            defaults={"quantity_packages": 200, "total_content": 5000.0}
        )
        if not created2:
            cls.inventory_ok.quantity_packages = 200
            cls.inventory_ok.total_content = 5000.0
            cls.inventory_ok.save()
        print(f"Inventario preparado para '{cls.product_expiring.name_prod}' en bodega principal.")

        print("Datos base cargados correctamente.\n")

    # -----------------------------------------------------
    # Configuración del cliente autenticado
    # -----------------------------------------------------
    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin)

    # -----------------------------------------------------
    # TC-NOTIF-01 — Notificación de Stock Bajo
    # -----------------------------------------------------
    def test_01_notificacion_stock_bajo(self):
        print("TC-NOTIF-01: VERIFICAR NOTIFICACIÓN DE STOCK BAJO")
        create_notifications()

        notif = Notification.objects.filter(
            notif_type="low_stock", user=self.admin
        ).first()

        self.assertIsNotNone(notif, "❌ No se generó notificación low_stock")
        self.assertIn("Urea", notif.message)
        self.assertFalse(notif.read)
        print("✅ TC-NOTIF-01: Notificación 'low_stock' creada correctamente.\n")

    # -----------------------------------------------------
    # TC-NOTIF-02 — Notificación por Vencimiento Próximo
    # -----------------------------------------------------
    def test_02_notificacion_vencimiento(self):
        print("TC-NOTIF-02: VERIFICAR NOTIFICACIÓN DE VENCIMIENTO PRÓXIMO")
        create_notifications()

        notif = Notification.objects.filter(
            notif_type="expiring", user=self.admin
        ).first()

        self.assertIsNotNone(notif, "❌ No se generó notificación expiring")
        self.assertIn("vence el", notif.message)
        self.assertFalse(notif.read)
        print("✅ TC-NOTIF-02: Notificación 'expiring' creada correctamente.\n")

    # -----------------------------------------------------
    # TC-NOTIF-03 — Marcar Notificaciones Como Leídas
    # -----------------------------------------------------
    def test_03_marcar_notificaciones_leidas(self):
        print("TC-NOTIF-03: VERIFICAR MARCADO DE NOTIFICACIONES COMO LEÍDAS")
        Notification.objects.create(
            user=self.admin,
            notif_type="low_stock",
            product=self.product_low,
            message="Prueba de lectura"
        )

        response = self.client.post(reverse("notification:mark_read"))
        self.assertEqual(response.status_code, 200)

        notif = Notification.objects.first()
        self.assertTrue(notif.read)
        self.assertIsNotNone(notif.read_at)
        print("✅ TC-NOTIF-03: Notificación marcada como leída correctamente.\n")

    # -----------------------------------------------------
    # TC-NOTIF-04 — Vista de Notificaciones (Listar)
    # -----------------------------------------------------
    def test_04_vista_lista_notificaciones(self):
        print("TC-NOTIF-04: VERIFICAR VISTA DE LISTADO DE NOTIFICACIONES")
        Notification.objects.create(
            user=self.admin,
            notif_type="expiring",
            product=self.product_expiring,
            message="Prueba UI expiring"
        )

        response = self.client.get(reverse("notification:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prueba UI expiring")
        print("✅ TC-NOTIF-04: Vista lista muestra notificaciones correctamente.\n")

    # -----------------------------------------------------
    # TC-NOTIF-05 — Prevención de Notificaciones Duplicadas
    # -----------------------------------------------------
    def test_05_evitar_notificaciones_duplicadas(self):
        print("TC-NOTIF-05: VERIFICAR PREVENCIÓN DE DUPLICADOS")
        Notification.objects.create(
            user=self.admin,
            notif_type="low_stock",
            product=self.product_low,
            message="Duplicado"
        )

        create_notifications()
        notifs = Notification.objects.filter(
            product=self.product_low, notif_type="low_stock"
        )
        self.assertEqual(notifs.count(), 1, "❌ Se creó una notificación duplicada.")
        print("✅ TC-NOTIF-05: Prevención de duplicados validada.\n")

    # -----------------------------------------------------
    # TC-NOTIF-06 — Endpoint check_notifications
    # -----------------------------------------------------
    def test_06_endpoint_check_notifications(self):
        print("TC-NOTIF-06: VERIFICAR ENDPOINT /check/ DE ALERTAS")
        create_notifications()
        response = self.client.get(reverse("notification:check_alerts"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("low_stock", data)
        self.assertIn("expiring", data)
        print("✅ TC-NOTIF-06: Endpoint check_notifications devuelve JSON correctamente.\n")
