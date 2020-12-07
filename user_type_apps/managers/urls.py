from django.urls import path, include
from django.conf import settings
from . import views as views

app_name = 'managers'

urlpatterns = [
    path('list', views.manager_list, name="manager_list"),
    path("add", views.manager_add, name="manager_add"),
    path('view/<pk>/', views.manager_view, name="manager_view"),
    path("edit/<pk>", views.manager_edit, name="manager_edit"),
    path("edit/<pk>/change_password/", views.change_password, name="manager_change_password"),
    path('team/list/<pk>/', views.my_employee_list, name="my_employee_list"),
    path('teamlead/list/<pk>/', views.my_team_list, name="my_team_list"),
]