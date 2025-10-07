from django.urls import path
from .views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView

app_name = "core"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/new/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
]


