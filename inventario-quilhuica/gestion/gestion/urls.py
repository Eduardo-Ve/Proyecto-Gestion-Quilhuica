"""
URL configuration for gestion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from login.views import registrar_usuario
from  django.conf.urls import handler400, handler403, handler404, handler500
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('core/', include('core.urls')),
    path('', include('core.urls')),
    path("register/", registrar_usuario, name="register"), 
    path('', include('product.urls')),  # Agrega esta línea
]
handler400 = "core.views.error_400"
handler403 = "core.views.error_403"
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"