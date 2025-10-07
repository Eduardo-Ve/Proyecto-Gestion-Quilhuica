from django.urls import path
from .views import (
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView
)

app_name = "product"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("new/", ProductCreateView.as_view(), name="product_create"),
    path("<int:pk>/edit/", ProductUpdateView.as_view(), name="product_update"),
    path("<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
]