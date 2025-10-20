from django.contrib import admin
from django.urls import path, include
from login.views import registrar_usuario
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
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    ]

handler400 = "core.views.error_400"
handler403 = "core.views.error_403"
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"