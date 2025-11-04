from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm
import re
from django.core.exceptions import ValidationError
from login.models import Usuario  # tu modelo de usuarios
from login.models import Role
from django.contrib.auth.forms import PasswordResetForm
from warehouse.models import Warehouse
import secrets
import string


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

# form de registro

User = get_user_model()

class RegistroUsuarioForm(forms.ModelForm):
    roles = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select,
        required=True,
        label="Rol"
    )

    casetas_asignadas = forms.ModelMultipleChoiceField(
    queryset=Warehouse.objects.filter(type='shed'),
    required=False,
    label="Casetas Asignadas",
    widget=forms.CheckboxSelectMultiple
    )


    class Meta:
        model = Usuario
        fields = ["nombre_usuario", "correo", "telefono", "roles", "casetas_asignadas"]
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'placeholder': 'Perez Cotapo'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'ejemplo@dominio.com'}),
            'telefono': forms.NumberInput(attrs={'placeholder': '931816450'}),
        }

    # --- Validaciones ---
    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data.get("nombre_usuario").strip()
        if Usuario.objects.filter(nombre_usuario__iexact=nombre_usuario).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return nombre_usuario.title()

    def clean_correo(self):
        correo = self.cleaned_data.get("correo")
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, correo):
            raise forms.ValidationError("Ingrese un correo electrónico válido.")
        if Usuario.objects.filter(correo__iexact=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo.lower()

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        patron = r'^[9]\d{8}$'
        if not re.match(patron, telefono):
            raise forms.ValidationError("Debe ingresar un número válido de 9 dígitos, ej: 930806450")
        return f"+56{telefono}"

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get("roles")
        casetas = cleaned_data.get("casetas_asignadas")

        if rol and rol.name_role == 'Encargado de caseta' and (not casetas or len(casetas) == 0):
            self.add_error('casetas_asignadas', 'Debe asignar una o más casetas para este rol.')
        
        return cleaned_data


    # --- Guardado con contraseña generada ---
    def save(self, commit=True):
        user = super().save(commit=False)

        # Generar contraseña temporal
        caracteres = string.ascii_letters + string.digits + string.punctuation
        temp_password = ''.join(secrets.choice(caracteres) for _ in range(10))
        user.set_password(temp_password)
        user.must_change_password = True

        if commit:
            user.save()
            user.roles.set([self.cleaned_data["roles"]])
            user.casetas_asignadas.set(self.cleaned_data.get('casetas_asignadas'))  #  <- Guardado ManyToMany.
            user._temp_password = temp_password  

        return user

User = get_user_model()
class CustomPasswordResetForm(PasswordResetForm):
  
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
   
    def get_users(self, email):
        """Busca usuarios usando el campo 'correo' del modelo."""
        active_users = Usuario._default_manager.filter(
            correo__iexact=email, 
            is_active=True
        )
        return (u for u in active_users if u.has_usable_password())