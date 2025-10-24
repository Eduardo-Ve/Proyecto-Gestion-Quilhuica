from django.urls import path
from . import views
app_name = 'warehouse' 
urlpatterns = [
    path('', views.caseta_list, name='caseta_list'),
    path('new/', views.caseta_create, name='caseta_create'),
    path('edit/<int:pk>/', views.caseta_edit, name='caseta_edit'),
    path('delete/<int:pk>/', views.caseta_delete, name='caseta_delete'),
    path('transfer-product/', views.transfer_product, name='transfer_product'),
    path('inventory-list/', views.inventory_list, name='inventory_list'),
    path('ajax/products/<int:warehouse_id>/', views.get_products_by_warehouse, name='get_products_by_warehouse'),

]