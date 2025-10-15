from django.contrib import admin
from django.urls import path, include
from login.views import registrar_usuario
from login.views import CustomPasswordResetView
from django.contrib.auth import views as auth_views
from  django.conf.urls import handler400, handler403, handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('', include('core.urls')),
    path("register/", registrar_usuario, name="register"), 
    path('products/', include(('product.urls', 'product'), namespace='product')),  
    path('warehouse/', include(('warehouse.urls', 'warehouse'), namespace='warehouse')), 
    path('base_desing/', include(('base.urls', 'base'), namespace='base')),  
    path('application/', include(('application.urls', 'application'), namespace='application')),
    path("reset_password/", CustomPasswordResetView.as_view(), name="reset_password"),
    path("reset_password_sent/", auth_views.PasswordResetDoneView.as_view(template_name="login/password_reset_sent.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="login/password_reset_form.html"), name="password_reset_confirm"),
    path("reset_password_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="login/password_reset_done.html"), name="password_reset_complete"),
    ]

handler400 = "core.views.error_400"
handler403 = "core.views.error_403"
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"