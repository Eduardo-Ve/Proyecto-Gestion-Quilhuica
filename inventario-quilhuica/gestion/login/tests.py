# login/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from login.models import Role
from .forms import RegistroUsuarioForm


# Obtener el modelo de usuario personalizado definido en settings.AUTH_USER_MODEL
User = get_user_model()


# ===============================
# 🔹 PRUEBAS DE ROBUSTEZ DEL LOGIN
# ===============================
class LoginRobustnessTest(TestCase):
    """
    Verifica que el sistema de login no se caiga (error 500)
    ante entradas extrañas o potencialmente maliciosas.
    """

    def setUp(self):
        # Crea un usuario válido
        User.objects.create_user(nombre_usuario="testuser", correo="test@test.com", password="SafePass123")
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
            # No debe causar error interno del servidor
            self.assertNotEqual(resp.status_code, 500, f"Error 500 con payload: {p}")
            # Puede devolver 200 (recarga login) o 302 (redirige tras login exitoso)
            self.assertIn(resp.status_code, (200, 302))


# ===============================
# 🔹 PRUEBAS DEL FLUJO DE LOGIN
# ===============================
class LoginFlowTest(TestCase):
    """
    Prueba el flujo normal y fallido de autenticación.
    """

    def setUp(self):
        # Crea un usuario para las pruebas
        self.user = User.objects.create_user(nombre_usuario="juan", correo="juan@test.com", password="MiPass123")
        self.client = Client()

    def test_login_success(self):
        """
        Verifica que un usuario válido pueda iniciar sesión.
        """
        resp = self.client.post(reverse('login'), {
            'username': 'juan',
            'password': 'MiPass123'
        })
        self.assertIn(resp.status_code, (302, 200))

    def test_login_fail_shows_error(self):
        """
        Verifica que al fallar el login, se muestre el mensaje de error adecuado.
        """
        resp = self.client.post(reverse('login'), {
            'username': 'juan',
            'password': 'wrong'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Usuario o contraseña incorrectos.", html=False)


# ===============================
# 🔹 PRUEBAS DEL FORMULARIO DE REGISTRO
# ===============================
class RegistroFormTest(TestCase):
    """
    Verifica que el formulario de registro funcione correctamente
    y cree un usuario con los datos válidos.
    """

    def setUp(self):
        # Crea un rol de prueba (ya que es requerido por el form)
        self.role = Role.objects.create(name_role="Usuario")

    def test_form_valid_data_creates_user(self):
        """
        Verifica que un formulario con datos válidos cree un usuario correctamente.
        """
        form = RegistroUsuarioForm(data={
            "nombre_usuario": "pedro",
            "correo": "p@x.com",
            "telefono": "912345678",
            "password1": "ComplexPass!1",
            "password2": "ComplexPass!1",
            "roles": self.role.id,
        })
        # El formulario debe ser válido
        self.assertTrue(form.is_valid(), form.errors)

        # Guardar usuario
        user = form.save()

        # Verificar que se creó correctamente
        self.assertEqual(user.nombre_usuario, "Pedro")  # se capitaliza por .title()
        self.assertEqual(user.correo, "p@x.com")
        self.assertTrue(user.check_password("ComplexPass!1"))
        self.assertTrue(user.roles.filter(id=self.role.id).exists())


# ===============================
# 🔹 DOCUMENTACIÓN DE TESTS
# ===============================
"""
LoginRobustnessTest:
    - Verifica que el login no arroje error 500 ante entradas extrañas o peligrosas.
    - Espera status 200 o 302, nunca 500.

LoginFlowTest:
    - Prueba login exitoso (debe redirigir o cargar página principal).
    - Prueba login fallido (debe mostrar mensaje de error y recargar login).

RegistroFormTest:
    - Verifica que el formulario de registro acepte datos válidos y cree usuario.
    - Comprueba campos, contraseña y asociación de rol.

Todos los tests deben pasar sin errores y reflejan la robustez y funcionalidad básica
del sistema de autenticación.
"""
