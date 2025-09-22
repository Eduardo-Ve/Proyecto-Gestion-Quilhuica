from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
import re
from login.models import Usuario  # tu modelo de usuarios

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

    class Meta:
        model = Usuario
        fields = ["nombre_usuario", "correo", "telefono", "cargo"]

    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data.get("nombre_usuario").strip()
        if Usuario.objects.filter(nombre_usuario__iexact=nombre_usuario).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return nombre_usuario.title()

    def clean_correo(self):
        correo = self.cleaned_data.get("correo")
        if Usuario.objects.filter(correo__iexact=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo.lower()

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        patron = r'^[9]\d{8}$'
        if not re.match(patron, telefono):
            raise forms.ValidationError("Debe ingresar un número válido de 9 dígitos, ej: 930806450")
        return f"+56 {telefono}"

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # guarda contraseña encriptada
        if commit:
            user.save()
        return user
