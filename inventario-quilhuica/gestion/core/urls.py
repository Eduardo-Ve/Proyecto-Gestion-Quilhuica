from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.index, name='index'),
    path('style/', views.style, name='style'),
    path("test-error/", test_error_page),
]