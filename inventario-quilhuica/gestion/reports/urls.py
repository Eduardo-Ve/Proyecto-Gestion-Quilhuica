from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportHomeView.as_view(), name="report_home"),
    path("export/", views.ExportReportView.as_view(), name="export_report"),
]