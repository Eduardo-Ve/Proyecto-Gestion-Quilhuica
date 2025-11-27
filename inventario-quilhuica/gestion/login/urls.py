# login/urls.py
from django.urls import path
from .views import CustomLoginView, logout_view, activar_cuenta

urlpatterns = [
    path("", CustomLoginView.as_view(template_name="login/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("activar/<uidb64>/<token>/", activar_cuenta, name="activar_cuenta"),
]
