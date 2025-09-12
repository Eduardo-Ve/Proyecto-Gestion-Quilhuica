from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RegistroUsuario(UserCreationForm):
    first_name = forms.CharField(
        max_length=20,
        help_text="Ingrese su nombre",
        label="Nombre",
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Juan'})
    )
    last_name = forms.CharField(
        max_length=20,
        help_text="Ingrese su apellido",
        label="Apellido",
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Pérez'})
    )
    email = forms.EmailField(
        max_length=120,
        help_text="Ingrese su correo",
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'})
    )
    phone = forms.CharField(
        max_length=12,
        help_text="Ingrese su celular (+569XXXXXXXX)",
        label="Teléfono",
        widget=forms.TextInput(attrs={'placeholder': '+56912345678'})
    )

    class Meta(UserCreationForm.Meta):
        model = User    
        fields = ("username", "first_name", "last_name", "email", "phone", "password1", "password2")
        labels = {
            "username": "Usuario o correo",
            "password1": "Contraseña",
            "password2": "Repetir contraseña",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Ej: eduardo123"}),
        }
        help_texts = {
            "username": "Requerido. 20 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.",
            "password1": "Su contraseña no puede ser muy similar a su otra información personal.<br>Su contraseña debe contener al menos 8 caracteres.<br>Su contraseña no puede ser una contraseña común.<br>Su contraseña no puede ser completamente numérica.",
            "password2": "Ingrese la misma contraseña que antes, para verificación.",
        }

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o correo",
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su usuario o correo'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'})
    )
    error_messages = {
        'invalid_login': "Usuario o contraseña incorrectos. Inténtelo nuevamente.",
        'inactive': "Esta cuenta está inactiva, contacte al administrador.",
    }