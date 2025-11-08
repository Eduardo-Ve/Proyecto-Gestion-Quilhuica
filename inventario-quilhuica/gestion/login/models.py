from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from warehouse.models import *

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError("El usuario debe tener un correo")
        correo = self.normalize_email(correo)
        user = self.model(nombre_usuario=nombre_usuario, correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, nombre_usuario, correo, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(nombre_usuario, correo, password, **extra_fields)
    
class Role(models.Model):
    name_role = models.CharField(max_length=100, unique=True)
    description_role = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name_role

class Usuario(AbstractBaseUser, PermissionsMixin):
    id_user = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=150, unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, related_name="usuarios", through="UserRole")
    objects = UsuarioManager()
    must_change_password = models.BooleanField(default=True)
    USERNAME_FIELD = "nombre_usuario"
    REQUIRED_FIELDS = ["correo"]
    ware_assig = models.ManyToManyField(
        Warehouse,
        blank=True,
        related_name="encargados_multiples",
        help_text="Casetas asignadas (solo aplica para Encargados de caseta)",
        limit_choices_to={'type': 'shed'}
    )
    @property
    def email(self):
        """Alias para compatibilidad con Django (usa el campo 'correo')"""
        return self.correo
    def has_role(self, role_name):
            """
            Verifica si el usuario tiene un rol específico (por nombre)
            o alguno de una lista de roles.
            """
            if isinstance(role_name, str):
                # Si se pasa un solo nombre de rol
                return self.roles.filter(name_role=role_name).exists()
            elif isinstance(role_name, list):
                # Si se pasa una lista de nombres de roles
                return self.roles.filter(name_role__in=role_name).exists()
            return False   
    @property
    def is_admin(self):
        """Propiedad para verificar fácilmente si es Administrador"""
        return self.has_role("Administrador")  

    @property
    def is_supervisor(self):
        """Propiedad para verificar fácilmente si es Supervisor"""
        return self.has_role("Supervisor")
    
class UserRole(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.nombre_usuario} - {self.role.name_role}"