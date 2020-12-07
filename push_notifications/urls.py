
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter

from . import viewsets as api
from . import views as views


app_name = 'push_notifications'


# API urls
api_urlpatterns = [
    path('v1/moblie_device', api.MobileDeviceAPIView.as_view()),
    path('v1/notifications', api.MobileNotificationListView.as_view()),
    path('v1/notifications/<pk>/', api.MobileNotificationUpdateView.as_view()),
    path('v1/notifications/<pk>/detail', api.MobileNotificationDetailView.as_view()),

]
# views url
urlpatterns = [
    path("push_notification_view", views.push_notification_view, name="push_notification_view"),
    path("push_notification_add", views.push_notification_add, name="push_notification_add"),
]

urlpatterns += [path('api/', include(api_urlpatterns))]

# router = DefaultRouter()
# router.register(r'v1/moblie_device', api.MobileDeviceViewSet, basename='moblie_device')
# urlpatterns = router.urls
