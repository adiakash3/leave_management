
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter

from . import viewsets as api
from . import views as views


app_name = 'reports'


# API urls
api_urlpatterns = [
    path('v1/employee_overtime', api.EmployeeOverTime.as_view()),

]

# views url
urlpatterns = [
    path("view", views.report_view, name="report_view"),
    path("shift_work_hours", views.shift_work_hours, name="shift_work_hours"),
    path("employees/leaves", views.employees_leave_report, name="employees_leave_report"),
    path("employees/<int:emp_id>/leaves/details", views.employees_leave_report_detail, name="employees_leave_report_detail"),
    path("employees/<int:emp_id>/<int:leave_type_id>/<int:fyl_config_id>/edit", views.update_leave_carry_cout, name="update_leave_carry_cout"),
]

urlpatterns += [path('api/', include(api_urlpatterns))]