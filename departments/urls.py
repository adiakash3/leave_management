from django.urls import path, include
from django.conf import settings

from . import views as web_views

app_name = 'departments'

urlpatterns = [
    path('list', web_views.department_list, name="department_list"),
    path('add', web_views.department_add, name="department_add"),
    path('<int:department_id>/edit/', web_views.department_edit, name="department_edit"),
    path('<int:department_id>/view/', web_views.department_view, name="department_view"),
    path('organisation/list', web_views.organisation_list, name="organisation_list"),
    path('organisation/<int:organisation_id>/view/', web_views.organisation_view, name="organisation_view"),
    path('organisation/<int:organisation_id>/edit/', web_views.organisation_edit, name="organisation_edit"),
]