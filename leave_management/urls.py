
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', include('dashboard.urls', namespace="dashboard")),
    path('accounts/', include('accounts.urls', namespace="accounts")),
    path('holidays/', include('holidays.urls', namespace="holidays")),
    path('leaves/', include('leaves.urls', namespace="leaves")),
    path('push_notifications/', include('push_notifications.urls', namespace="push_notifications")),
    path('managers/', include('user_type_apps.managers.urls', namespace="managers")),
    path('employees/', include('user_type_apps.employees.urls', namespace="employees")),
    path('team_leaders/', include('user_type_apps.team_leaders.urls', namespace="team_leaders")),
    path('shifts/', include('shifts.urls', namespace="shifts")),
    path('reports/', include('reports.urls', namespace="reports")),
    path('departments/', include('departments.urls', namespace="departments")),
    path('emails/', include('emails.urls', namespace="emails")),
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)