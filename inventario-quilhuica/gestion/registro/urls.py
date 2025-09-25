from django.contrib import admin
from django.urls import path
from registro.views import registrar_usuario, success_view
urlpatterns = [
    path('',registrar_usuario, name='registrar_usuario'),  # página para registrar usuarios
    path("success/",success_view, name="success"),  # página de éxito
]