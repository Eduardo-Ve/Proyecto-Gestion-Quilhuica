from datetime import date, timedelta

from django.test import TestCase, Client
from django.urls import reverse

from login.models import Role, Usuario, UserRole
from warehouse.models import Warehouse, Inventory, Movement
from product.models import Product, Category, Presentation


class ProductFunctionalTests(TestCase):
    """
    Tests funcionales para productos (TC-PROD-01 ... TC-PROD-04)
    Ejecutar: py.exe manage.py test product --verbosity 2
    """

    def setUp(self):
        # Bodega principal
        self.main_warehouse = Warehouse.objects.create(
            name_ware="Bodega Principal", type="main"
        )

        # Usuario Administrador
        self.role_admin = Role.objects.create(name_role="Administrador")
        self.user = Usuario.objects.create_user(
            nombre_usuario="testadmin",
            correo="testadmin@example.com",
            password="testpass"
        )
        UserRole.objects.create(user=self.user, role=self.role_admin)

        self.client = Client()
        self.client.force_login(self.user)

        # Entidades base
        self.category = Category.objects.create(name_cat="CatEx", description_cat="Desc")
        self.presentation = Presentation.objects.create(
            package_type="saco", content_value=10, content_unit="kg"
        )

    # ===============================================================
    # TC-PROD-01 — Crear producto + nueva categoría + nueva presentación
    # ===============================================================
    def test_tc_prod_01_create_product_with_new_category_and_presentation(self):

        url = reverse("product:product_create")
        expire = (date.today() + timedelta(days=365)).isoformat()

        data = {
            "name_prod": "ProductoPrueba",
            "create_new_category": "on",
            "new_category_name": "NuevaCatT1",
            "new_category_description": "Creada desde test",
            "create_new_presentation": "on",
            "package_type": "saco",
            "content_value": "5",
            "content_unit": "kg",
            "expire_at": expire,
            "stock_inicial": "3"
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        prod = Product.objects.filter(name_prod="ProductoPrueba").first()
        self.assertIsNotNone(prod)

        # Categoría y presentación creadas
        self.assertTrue(Category.objects.filter(name_cat="NuevaCatT1").exists())
        self.assertTrue(Presentation.objects.filter(content_value=5).exists())

        # Inventario creado
        inv = Inventory.objects.filter(
            product=prod, warehouse=self.main_warehouse
        ).first()
        self.assertIsNotNone(inv)
        self.assertEqual(inv.quantity_packages, 3)

        # Movimiento inicial
        mov = Movement.objects.filter(product=prod).first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.quantity, 3)

    # ===============================================================
    # TC-PROD-02 — Editar producto y ajustar stock
    # ===============================================================
    def test_tc_prod_02_edit_product_updates_fields_and_stock(self):

        prod = Product.objects.create(
            name_prod="ProdEditar",
            category=self.category,
            presentation=self.presentation,
            expire_at=(date.today() + timedelta(days=200))
        )

        # Inventario inicial (usamos get_or_create para evitar UNIQUE)
        inv, created = Inventory.objects.get_or_create(
            product=prod,
            presentation=self.presentation,
            warehouse=self.main_warehouse,
            defaults={"quantity_packages": 2}
        )

        if not created:
            inv.quantity_packages = 2
            inv.save()

        url = reverse("product:product_update", args=[prod.product_id])
        expire2 = (date.today() + timedelta(days=400)).isoformat()

        data = {
            "name_prod": "ProdEditarMod",
            "category": self.category.pk,
            "presentation": self.presentation.pk,
            "expire_at": expire2,
            "stock_inicial": "5"
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        prod.refresh_from_db()
        self.assertEqual(prod.name_prod, "ProdEditarMod")

        inv.refresh_from_db()
        self.assertEqual(inv.quantity_packages, 5)

        mov = Movement.objects.filter(product=prod).order_by("-id").first()
        self.assertEqual(mov.quantity, 3)  # ajuste 5 - 2

    # ===============================================================
    # TC-PROD-03 — Soft delete y mantener movimientos
    # ===============================================================
    def test_tc_prod_03_delete_product_soft_and_preserve_movements(self):

        prod = Product.objects.create(
            name_prod="ProdDelete",
            category=self.category,
            presentation=self.presentation,
            expire_at=(date.today() + timedelta(days=100))
        )

        inv, created = Inventory.objects.get_or_create(
            product=prod,
            presentation=self.presentation,
            warehouse=self.main_warehouse,
            defaults={"quantity_packages": 4}
        )
        if not created:
            inv.quantity_packages = 4
            inv.save()

        Movement.objects.create(
            product=prod,
            presentation=self.presentation,
            ware_origin=None,
            ware_destin=self.main_warehouse,
            movement_type="entrada",
            quantity=4,
            moved_by=self.user,
            description="Inicial"
        )

        url = reverse("product:product_delete", args=[prod.product_id])
        self.client.get(url)

        self.client.post(url, follow=True)

        prod.refresh_from_db()
        self.assertFalse(prod.is_active)

        self.assertTrue(Movement.objects.filter(product=prod).exists())

    # ===============================================================
    # TC-PROD-04 — Crear categoría usando checkbox
    # ===============================================================
    def test_tc_prod_04_create_category_checkbox_behavior(self):

        url = reverse("product:product_create")
        expire = (date.today() + timedelta(days=365)).isoformat()

        data = {
            "name_prod": "ProdCatCheck",
            "create_new_category": "on",
            "new_category_name": "CategoriaDesdeCheckbox",
            "new_category_description": "descr",
            "category": "",
            "presentation": self.presentation.pk,
            "expire_at": expire,
            "stock_inicial": "0"
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        prod = Product.objects.filter(name_prod="ProdCatCheck").first()
        self.assertIsNotNone(prod)
        self.assertEqual(prod.category.name_cat, "CategoriaDesdeCheckbox")
