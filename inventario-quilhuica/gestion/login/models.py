from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

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

    USERNAME_FIELD = "nombre_usuario"
    REQUIRED_FIELDS = ["correo"]

    class Meta:
        db_table = "usuario"


class UserRole(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.nombre_usuario} - {self.role.name_role}"