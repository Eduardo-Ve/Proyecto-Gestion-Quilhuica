from django import forms
from .models import ProblemReport

class ReportarProblemaForm(forms.ModelForm):
    class Meta:
        model = ProblemReport
        fields = ['module', 'subject', 'description', 'priority']
        widgets = {
            'module': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Error al guardar aplicación'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el problema encontrado...'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'module': 'Módulo afectado',
            'subject': 'Asunto del problema',
            'description': 'Descripción detallada',
            'priority': 'Prioridad',
        }
