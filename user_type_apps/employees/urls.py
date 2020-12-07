from django.urls import path, include
from django.conf import settings
from . import views as views

app_name = 'employees'

urlpatterns = [
    path('list', views.employee_list, name="employee_list"),
    path("add", views.employee_add, name="employee_add"),
    path('view/<pk>/', views.employee_view, name="employee_view"),
    path("edit/<pk>", views.employee_edit, name="employee_edit"),
    path("edit/<pk>/change_password/", views.change_password, name="employee_change_password"),
    path('<int:employee_id>/report', views.employee_report, name="employee_report"),
    path('list/report', views.employee_report_list, name="employee_report_list"),
    
]