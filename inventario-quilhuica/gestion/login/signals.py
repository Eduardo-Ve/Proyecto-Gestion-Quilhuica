from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Usuario  # Asegúrate que el import sea correcto

# Esta señal se "dispara" cada vez que el campo 'roles' del Usuario cambia
@receiver(m2m_changed, sender=Usuario.roles.through)
def actualizar_estado_staff(sender, instance, action, **kwargs):
    """
    Actualiza el campo 'is_staff' del usuario basado en
    si tiene el rol 'Administrador'.
    """
    
    # 'instance' es el objeto Usuario que se está modificando.
    
    # Solo nos interesa actuar DESPUÉS de que se añadan, quiten o limpien los roles
    if action in ("post_add", "post_remove", "post_clear"):
        
        # Un Superusuario SIEMPRE debe ser 'is_staff', 
        # independientemente de sus roles.
        if instance.is_superuser:
            if not instance.is_staff:
                instance.is_staff = True
                instance.save(update_fields=['is_staff'])
            return # No hacemos nada más

        # Para usuarios normales, sincronizamos 'is_staff' con el rol
        # Usamos el método .has_role() que ya tienes en tu modelo
        tiene_rol_admin = instance.has_role("Administrador")
        
        # Si el estado de 'is_staff' es diferente al de tener el rol, lo actualizamos
        if instance.is_staff != tiene_rol_admin:
            instance.is_staff = tiene_rol_admin
            instance.save(update_fields=['is_staff'])