# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class LoginRobustnessTest(TestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", password="SafePass123")
        self.client = Client()

    def test_login_with_special_chars_should_not_500(self):
        url = reverse('login')  
        payloads = [
            "''''\"\"--/**/\\\\\\",
            "a" * 2000,
            "%$#@!*()_+|}{:<>?~`"
        ]
        for p in payloads:
            resp = self.client.post(url, {'username': p, 'password': p})
            self.assertNotEqual(resp.status_code, 500, f"Server error con payload {p}")
            
            self.assertIn(resp.status_code, (200, 302))
class LoginFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="juan", password="MiPass123")
        self.client = Client()

    def test_login_success(self):
        resp = self.client.post(reverse('login'), {'username': 'juan', 'password': 'MiPass123'})
        
        self.assertIn(resp.status_code, (302, 200))

    def test_login_fail_shows_error(self):
        resp = self.client.post(reverse('login'), {'username': 'juan', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Usuario o contraseña incorrectos.", html=False)
from .forms import RegistroUsuario

class RegistroFormTest(TestCase):
    def test_form_valid_data_creates_user(self):
        form = RegistroUsuario(data={
            "username": "pedro",
            "first_name": "Pedro",
            "last_name": "Perez",
            "email": "p@x.com",
            "phone": "+56912345678",
            "password1": "ComplexPass!1",
            "password2": "ComplexPass!1",
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "pedro")

# ---------------------------------------------
# Documentación de los tests:
# (creo que me salte un poco aca, o sea esto es mas adelante pero me emocione trabajando)
# LoginRobustnessTest:
#   - Verifica que el login no arroje error 500 ante entradas extrañas o peligrosas.
#   - Espera status 200 o 302, nunca 500.
#
# LoginFlowTest:
#   - Prueba login exitoso (debe redirigir o cargar página principal).
#   - Prueba login fallido (debe mostrar mensaje de error y recargar login).
#
# RegistroFormTest:
#   - Verifica que el formulario de registro acepte datos válidos y cree usuario.
#   - El formulario debe ser válido con datos correctos.
#
# Todos los tests deben pasar sin errores y reflejan robustez y funcionalidad básica del sistema de autenticación.
# deberia escribir esto en un documento aparte pero bueno 
# ---------------------------------------------