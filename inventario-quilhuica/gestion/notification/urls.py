from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('check/', views.check_notifications, name='check_alerts'),
    path('mark-read/', views.mark_notifications_read, name='mark_read'),
]
