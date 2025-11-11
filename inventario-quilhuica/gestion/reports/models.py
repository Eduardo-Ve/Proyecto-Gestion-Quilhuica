from django.db import models
from django.conf import settings

class ProblemReport(models.Model):
    MODULE_CHOICES = [
        ('application', 'Aplicaciones'),
        ('warehouse', 'Casetas / Inventario'),
        ('product', 'Productos'),
        ('notification', 'Notificaciones'),
        ('reports', 'Reportes'),
        ('other', 'Otro'),
    ]

    PRIORITY_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_review', 'En Revisión'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.CharField(max_length=30, choices=MODULE_CHOICES)
    subject = models.CharField(max_length=100, verbose_name="Asunto")
    description = models.TextField(verbose_name="Descripción")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='media')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True, null=True, verbose_name="Comentario del administrador")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reporte de problema"
        verbose_name_plural = "Reportes de problemas"

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.subject} ({self.user})"
