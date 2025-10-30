# dashboard/urls.py
from django.urls import path
from . import views
from .views import * 

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("dashboard/activity-feed/", views.activity_feed_api, name="activity_feed_api"),
    path("test-error/", test_error_page),

]