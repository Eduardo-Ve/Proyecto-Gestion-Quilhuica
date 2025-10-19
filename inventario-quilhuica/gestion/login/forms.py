from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm
import re
from django.core.exceptions import ValidationError
from login.models import Usuario  # tu modelo de usuarios
from login.models import Role
from django.contrib.auth.forms import PasswordResetForm
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

# form de registro


class RegistroUsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña", 
        widget=forms.PasswordInput,
        help_text="Ingrese una contraseña segura."
    )
    password2 = forms.CharField(
        label="Confirmar contraseña", 
        widget=forms.PasswordInput,
        help_text="Ingrese la misma contraseña para confirmar."
    )
    
    roles = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select,   
        required=True
    )
    caseta_asignada = forms.ModelChoiceField(
            # El queryset filtra para mostrar SÓLO las bodegas de tipo 'shed'
            queryset=Warehouse.objects.filter(type='shed'),
            required=False,  # Es opcional a nivel de formulario
            label="Caseta Asignada",
            help_text="Requerido solo si el rol es 'Encargado de caseta'."
        )
    
    class Meta:
        model = Usuario
        fields = ["nombre_usuario", "correo", "telefono"]
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'placeholder': 'Perez Cotapo'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'ejemplo_usuario@dominio.com'}),
            'telefono': forms.NumberInput(attrs={'placeholder': '931816450'}),
        }

    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data.get("nombre_usuario").strip()
        if Usuario.objects.filter(nombre_usuario__iexact=nombre_usuario).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return nombre_usuario.title()

    def clean_correo(self):
        correo = self.cleaned_data.get("correo")

        # Regex con cerradura de Kleene (usuario + dominio + TLD(estuve 1 hora craneando esto)) 
        # creo que aqui deberia validar de otra forma igual (nota de Eduardo)
        # por ejemplo: podria hacer un tipo ping a un servidor de correo para validar que existe
        # o usar una libreria externa que haga eso como un checker de correos validados 
        # pero por ahora esto sirve
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
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        rol = cleaned_data.get("roles")
        caseta = cleaned_data.get("caseta_asignada")

        if rol:
            # Si el rol es 'Encargado de caseta', la caseta es obligatoria
            if rol.name_role == 'Encargado de caseta':
                if not caseta:
                    # Asigna el error al campo específico 'caseta_asignada'
                    self.add_error('caseta_asignada', 
                                   'Debe asignar una caseta para el rol "Encargado de caseta".')
            
            # Si es Admin o Auditor, nos aseguramos de que la caseta sea Nula
            elif rol.name_role in ['Administrador', 'Auditoria']:
                if caseta:
                    # Si el usuario seleccionó una por error, la limpiamos
                    cleaned_data['caseta_asignada'] = None
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # guarda contraseña encriptada
        user.caseta_asignada = self.cleaned_data.get('caseta_asignada')
        if commit:
            user.save()
            if self.cleaned_data.get("roles"):
                user.roles.set([self.cleaned_data["roles"]])  # crea registros en UserRole
        
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


