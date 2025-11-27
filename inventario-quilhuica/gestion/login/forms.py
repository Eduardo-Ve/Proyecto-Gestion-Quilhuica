from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from login.models import Usuario, Role  # tu modelo de usuarios y roles
from warehouse.models import Warehouse



User = get_user_model()


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o correo",
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su usuario o correo'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña', 'id': 'password'})
    )
    error_messages = {
        'invalid_login': "Usuario o contraseña incorrectos. Inténtelo nuevamente.",
        'inactive': "Esta cuenta está inactiva, contacte al administrador.",
    }


# ==========================
#   FORM DE REGISTRO
# ==========================

class RegistroUsuarioForm(forms.ModelForm):
    roles = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        label="Rol",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    ware_assig = forms.ModelMultipleChoiceField(
        queryset=Warehouse.objects.none(),
        required=False,
        label="Casetas Asignadas",
        widget=forms.SelectMultiple(
            attrs={'class': 'form-select', 'id': 'id_ware_assig'}
        )
    )

    class Meta:
        model = Usuario
        fields = ["nombre_usuario", "correo", "telefono", "roles", "ware_assig"]
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'placeholder': 'Perez Cotapo',
                'class': 'form-control'
            }),
            'correo': forms.EmailInput(attrs={
                'placeholder': 'ejemplo@dominio.com',
                'class': 'form-control'
            }),
            'telefono': forms.NumberInput(attrs={
                'placeholder': '931816450',
                'class': 'form-control'
            }),
            'roles': forms.Select(attrs={'class': 'form-select'}),
            'ware_assig': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ware_assig'].queryset = Warehouse.objects.filter(type='shed', activo=True)

    # --- Validaciones ---

    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data.get("nombre_usuario").strip()
        if Usuario.objects.filter(nombre_usuario__iexact=nombre_usuario).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return nombre_usuario.title()

    def clean_correo(self):
        correo = self.cleaned_data.get("correo")
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not correo:
            raise forms.ValidationError("El correo electrónico es obligatorio.")

        if not re.match(patron, correo):
            raise forms.ValidationError("Ingrese un correo electrónico válido.")

        if Usuario.objects.filter(correo__iexact=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return correo.lower()

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        patron = r'^[9]\d{8}$'

        if not telefono:
            raise forms.ValidationError("Debe ingresar un número de teléfono.")

        if not re.match(patron, str(telefono)):
            raise forms.ValidationError("Debe ingresar un número válido de 9 dígitos, ej: 930806450")

        return f"+56{telefono}"

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get("roles")
        casetas = cleaned_data.get("ware_assig")
        if rol and rol.name_role == 'Encargado de caseta' and (not casetas or len(casetas) == 0):
            self.add_error('ware_assig', 'Debe asignar una o más casetas para este rol.')
        return cleaned_data

    # --- Guardado con contraseña generada ---
    def save(self, commit=True):
        user = super().save(commit=False)

        # Nuevo flujo: cuenta inactiva y sin contraseña usable
        user.is_active = False
        user.set_unusable_password()  # no puede loguearse aún

        if commit:
            user.save()
            # roles: ModelChoice → lo pasas a ManyToMany con set
            user.roles.set([self.cleaned_data["roles"]])
            user.ware_assig.set(self.cleaned_data.get('ware_assig'))

        return user


# ==========================
#   RESET DE CONTRASEÑA
# ==========================

class CustomPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

    def get_users(self, email):
        """
        Busca usuarios usando el campo 'correo' del modelo Usuario,
        en lugar de usar User.email.
        """
        active_users = Usuario._default_manager.filter(
            correo__iexact=email,
            is_active=True
        )
        return (u for u in active_users if u.has_usable_password())


# =====================================
#   NUEVOS FORMULARIOS PEDIDOS
# =====================================

class AdminEditUserForm(forms.ModelForm):
    """
    Formulario que usa el ADMIN para editar:
      - Roles (M2M)
      - Casetas asignadas (ware_assig, M2M)
    """
    class Meta:
        model = Usuario
        fields = ['roles', 'ware_assig']  # solo lo que puede editar el admin

        widgets = {
            'roles': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'ware_assig': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'id': 'id_ware_assig'  # para que TomSelect lo tome en el template admin_edit_user
            }),
        }

        labels = {
            'roles': 'Roles',
            'ware_assig': 'Casetas Asignadas',
        }


class UserEditProfileForm(forms.ModelForm):
    """
    Formulario para que el usuario edite su propio perfil:
      - correo
      - telefono
    """
    class Meta:
        model = Usuario
        fields = ['correo', 'telefono']   # solo estos se pueden editar

        widgets = {
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@dominio.com'
            }),
            'telefono': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '931816450'
            }),
        }
