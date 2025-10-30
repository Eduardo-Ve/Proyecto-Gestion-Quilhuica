from django.urls import path
from .views import *
app_name = "product"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("new/", ProductCreateView.as_view(), name="product_create"),
    path("<int:pk>/edit/", ProductUpdateView.as_view(), name="product_update"),
    path("<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path('add_stock/', StockAddView.as_view(), name='add_stock'),

]
