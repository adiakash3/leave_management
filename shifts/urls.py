
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter

from . import viewsets as api
from . import views as views

app_name = 'shifts'


# API urls
api_urlpatterns = [
    path('v1/my_attendance', api.MyAttendanceList.as_view()),
    path('v1/my_shifts', api.MyShiftListView.as_view()),
    path('v1/late_exempt_queues', api.LateExemptsQueueListView.as_view()),
    path('v1/late_exempt_queues/<int:pk>/', api.LateExemptsQueueDetailView.as_view()),
    path('v1/apply_late_exempt', api.apply_late_exempt),
    path('v1/applied_late_exempt/<int:pk>', api.AppliedLateExemptDetails.as_view()),
    path('v1/applied_late_exempt_list', api.AppliedLateExemptListView.as_view()),
]

# views url
urlpatterns = [
    path('list', views.shift_list, name="shift_list"),
    path("add", views.shift_add, name="shift_add"),
    path("<int:shift_id>/edit", views.shift_edit, name="shift_edit"),
    path('<int:shift_id>/view', views.shift_view, name="shift_view"),
    path("shift_csv_import", views.shift_csv_import, name="shift_csv_import"),
    path("import_employee_attendance", views.import_employee_attendance, name="import_employee_attendance"),
    path("import_assign_employee_shift", views.import_assign_employee_shift, name="import_assign_employee_shift"),

    path('breaks/list', views.break_list, name="break_list"),
    path("breaks/add", views.break_add, name="break_add"),
    path("breaks/<int:break_id>/edit", views.break_edit, name="break_edit"),
    path('breaks/<int:break_id>/view', views.break_view, name="break_view"),
    path("employee_shift/add", views.employee_shift_add, name="employee_shift_add"),
    path("employee_shift/list", views.employee_shift_list, name="employee_shift_list"),
]

urlpatterns += [path('api/', include(api_urlpatterns))]