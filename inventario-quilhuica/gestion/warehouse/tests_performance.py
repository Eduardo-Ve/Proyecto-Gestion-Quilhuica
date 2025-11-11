# gestion/warehouse/tests_performance.py
import time
from django.test import TestCase, Client
from django.utils import timezone
from login.models import Usuario, Role
from warehouse.models import Warehouse

class PerformanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear usuario administrador y login automático
        role_admin = Role.objects.create(name_role="Administrador")
        cls.user = Usuario.objects.create_user(
            nombre_usuario="admin",
            correo="admin@test.com",
            password="admin123"
        )
        cls.user.roles.add(role_admin)

        # Crear una bodega principal (evita warning)
        Warehouse.objects.create(name_ware="Bodega Principal", type="main")

    def setUp(self):
        self.client = Client()
        self.client.login(nombre_usuario="admin", password="admin123")

    def medir_tiempo(self, url):
        inicio = time.perf_counter()
        resp = self.client.get(url)
        fin = time.perf_counter()
        duracion_ms = (fin - inicio) * 1000
        print(f"\n➡️ {url}: {duracion_ms:.2f} ms (status {resp.status_code})")
        return resp.status_code, duracion_ms


    def test_vistas_criticas(self):
        vistas = [
            ("/login/", "Login"),
            ("/warehouse/", "Módulo Warehouse"),
            ("/reports/", "Reportes"),
            ("/", "Dashboard Principal"),
        ]
        for url, nombre in vistas:
            code, dur = self.medir_tiempo(url)
            print(f"{nombre}: {dur:.2f} ms (status {code})")
            self.assertEqual(code, 200, f"{nombre} devolvió {code}")
            self.assertLessEqual(dur, 800, f"{nombre} tardó {dur:.2f} ms (> 800 ms)")
    def test_export_csv_performance(self):
        """
        NF-PERF-02: Verifica que la exportación CSV (reportes de movimientos)
        se complete en menos de 5 segundos.
        """
        import time

        url = "/reports/export/?report=movimientos&export=csv&start=2025-10-11&end=2025-11-10&user=&warehouse="
        inicio = time.perf_counter()
        resp = self.client.get(url)
        fin = time.perf_counter()
        duracion = fin - inicio

        print(f"\n Exportación CSV: {duracion:.2f} s (status {resp.status_code})")

        # Validaciones básicas
        self.assertEqual(resp.status_code, 200, "Error en la exportación CSV")
        self.assertLessEqual(duracion, 5, f"Exportación tardó {duracion:.2f} s (> 5 s)")

        # Validar encabezado de tipo de archivo
        self.assertIn("text/csv", resp["Content-Type"], "El archivo exportado no es CSV")
