from django.contrib import admin
from django.urls import path, include
from login.views import registrar_usuario
from login.views import CustomPasswordResetView
from django.contrib.auth import views as auth_views
from  django.conf.urls import handler400, handler403, handler404, handler500
from django.views.generic import TemplateView
from login.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('', include('core.urls')),
    path("register/", registrar_usuario, name="register"), 
    path('products/', include(('product.urls', 'product'), namespace='product')),  
    path('warehouse/', include(('warehouse.urls', 'warehouse'), namespace='warehouse')), 
    path('base_desing/', include(('base.urls', 'base'), namespace='base')),  
    path('application/', include(('application.urls', 'application'), namespace='application')),
    path("notification/", include("notification.urls")),
    path("reports/", include("reports.urls")),
    path('cambiar-contrasena-inicial/', change_new_password, name='cambiar_contrasena_inicial'),
    path("", include("dashboard.urls")),

    path("reset_password/",
         CustomPasswordResetView.as_view(  # ya usa tu form + template propio
             template_name="login/password_reset_form.html"
         ),
         name="reset_password"),

    path("reset_password_sent/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="login/password_reset_sent.html"   # ya lo tienes
         ),
         name="password_reset_done"),

    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="login/password_reset.html"        # usa tu archivo existente
         ),
         name="password_reset_confirm"),

    path("reset_password_complete/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="login/password_reset_done.html"   # reutiliza si no tienes 'complete'
         ),
         name="password_reset_complete"),
    ]



handler400 = "core.views.error_400"
handler403 = "core.views.error_403"
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"