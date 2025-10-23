from django.urls import path
from . import views

app_name = 'application'

urlpatterns = [
    path('new/', views.create_application, name='create_application'),
    path('confirm/', views.confirm_application, name='confirm_application'),
    path('cancel/', views.cancel_application, name='cancel_application'),
    path("api/products/", views.get_products_by_warehouse, name="get_products_by_warehouse"),
]