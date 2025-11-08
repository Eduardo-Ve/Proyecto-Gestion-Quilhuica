from django.urls import path
from . import views

app_name = "product"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("new/", views.ProductCreateView.as_view(), name="product_create"),
    path("<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("add_stock/", views.StockAddView.as_view(), name="add_stock"),
    path("inactive/", views.product_inactive_list, name="product_inactive_list"),
    path("reactivate/<int:pk>/", views.product_reactivate, name="product_reactivate"),
]
