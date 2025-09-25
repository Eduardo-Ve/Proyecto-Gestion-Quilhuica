from django.urls import path
from login.views import *

urlpatterns = [
    path('', CustomLoginView.as_view(template_name='login/login.html'), name="login"),
    path('logout/', logout_view, name='logout'),
]
