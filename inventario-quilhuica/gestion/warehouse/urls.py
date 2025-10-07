from django.urls import path
from . import views

urlpatterns = [
    path('casetas/', views.caseta_list, name='caseta_list'),
    path('casetas/nueva/', views.caseta_create, name='caseta_create'),
    path('casetas/editar/<int:pk>/', views.caseta_edit, name='caseta_edit'),
    path('casetas/eliminar/<int:pk>/', views.caseta_delete, name='caseta_delete'),
    path('casetas/productos/', views.productos_por_caseta, name='productos_por_caseta'),
    path('transferir-producto/', views.transfer_product, name='transfer_product'),
]