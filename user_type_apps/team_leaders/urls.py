from django.urls import path, include
from django.conf import settings
from . import views as views

app_name = 'team_leaders'

urlpatterns = [
    path('list', views.team_leader_list, name="team_leader_list"),
    path("add", views.team_leader_add, name="team_leader_add"),
    path('view/<pk>/', views.team_leader_view, name="team_leader_view"),
    path("edit/<pk>", views.team_leader_edit, name="team_leader_edit"),
    path("edit/<pk>/change_password/", views.change_password, name="team_leader_change_password"),
    path('team/list/<pk>/', views.my_employee_list, name="my_employee_list"),
]