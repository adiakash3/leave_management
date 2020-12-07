from django.urls import path, include
from django.conf import settings
from . import viewsets as api
from . import views as views

app_name = 'holidays'

api_urlpatterns = [
    path('v1/holidays', api.HolidayListView.as_view(), name="holiday_list"), 
]

urlpatterns = [path('api/', include(api_urlpatterns))]



urlpatterns += [
    path('list', views.holiday_list, name="holiday_list"),
    path("add", views.holiday_add, name="holiday_add"),
    path("<int:holiday_id>/edit/", views.holiday_edit, name="holiday_edit"),
    path('<int:holiday_id>/view/', views.holiday_view, name="holiday_view"),



]