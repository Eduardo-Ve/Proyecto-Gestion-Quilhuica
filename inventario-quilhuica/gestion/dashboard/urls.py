# dashboard/urls.py
from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("dashboard/", views.dashboard, name="home"),
]