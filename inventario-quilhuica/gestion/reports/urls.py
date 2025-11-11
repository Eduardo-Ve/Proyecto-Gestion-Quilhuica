from django.urls import path
from . import views


app_name = "reports"

urlpatterns = [
    path("", views.ReportHomeView.as_view(), name="report_home"),
    path("export/", views.ExportReportView.as_view(), name="export_report"),
    path('report-problem/', views.reportar_problema, name='reportar_problema'),
    path('admin-panel/', views.admin_problem_panel, name='admin_problem_panel'),
    path('change-status/<int:pk>/', views.change_report_status, name='change_report_status'),
]