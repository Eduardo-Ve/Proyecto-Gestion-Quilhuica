from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

#  Imports específicos de login
from login import views as login_views
from login.views import registrar_usuario, CustomPasswordResetView, change_new_password

from django.conf.urls import handler400, handler403, handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de la app login
    path('login/', include('login.urls')),

    # Registro de nuevo usuario (ya lo tenías)
    path("register/", registrar_usuario, name="register"),

    # NUEVAS RUTAS DE PERFIL / GESTIÓN DE USUARIOS
    path('edit_profile/', login_views.user_edit_profile, name='user_edit_profile'),
    path('users/', login_views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', login_views.admin_edit_user, name='admin_edit_user'),
    path('users/<int:user_id>/deactivate/', login_views.deactivate_user, name='deactivate_user'),
    path('users/<int:user_id>/activate/', login_views.activate_user, name='activate_user'),

    # Otras apps
    path('products/', include(('product.urls', 'product'), namespace='product')),
    path('warehouse/', include(('warehouse.urls', 'warehouse'), namespace='warehouse')),
    path('base_desing/', include(('base.urls', 'base'), namespace='base')),
    path('application/', include(('application.urls', 'application'), namespace='application')),
    path("notification/", include("notification.urls")),
    path("reports/", include("reports.urls")),

    # Cambio de contraseña inicial
    path('cambiar-contrasena-inicial/', change_new_password, name='cambiar_contrasena_inicial'),

    # Dashboard (home en "/")
    path("", include("dashboard.urls")),

    # Reset de contraseña
    path(
        "reset_password/",
        CustomPasswordResetView.as_view(
            template_name="login/password_reset_form.html"
        ),
        name="reset_password"
    ),

    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="login/password_reset_sent.html"
        ),
        name="password_reset_done"
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="login/password_reset.html"
        ),
        name="password_reset_confirm"
    ),

    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="login/password_reset_done.html"
        ),
        name="password_reset_complete"
    ),
        path(
    'sw.js',
    TemplateView.as_view(
        template_name="base/sw.js",
        content_type='application/javascript'
    ),
    name='sw.js'
),
]


handler400 = "dashboard.views.error_400"
handler403 = "dashboard.views.error_403"
handler404 = "dashboard.views.error_404"
handler500 = "dashboard.views.error_500"
