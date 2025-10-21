# login/urls.py
from django.urls import path
from login.views import CustomLoginView, logout_view



urlpatterns = [
    path('', CustomLoginView.as_view(template_name='login/login.html'), name="login"),
    path('logout/', logout_view, name='logout'),
]

