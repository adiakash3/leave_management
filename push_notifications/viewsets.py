from rest_framework import permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import mixins, GenericViewSet, generics
from .models import *
from .paginations import *
from .serializers import *


class MobileDeviceAPIView(APIView):
    """
    A viewset for viewing and editing user devices.
    """
    read_serializer_class = MobileDeviceReadSerializer
    write_serializer_class = MobileDeviceWriteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        """
        Return user device details
        """
        mobile_device, is_created = MobileDevice.objects.get_or_create(participant=request.user)
        mobile_device_serializer = self.read_serializer_class(mobile_device)
        return Response(mobile_device_serializer.data)
    
    def put(self, request, format=None):
        """
        Save user mobile fcm token
        """
        mobile_device, is_created = MobileDevice.objects.get_or_create(participant=request.user)
        mobile_device_serializer = self.write_serializer_class(mobile_device, data=request.data)
        mobile_device_serializer.is_valid(raise_exception=True)
        mobile_device_serializer.save()
        res = {
            "message" : "Fcm token updated successfully "
        }
        return Response(res)
    
    
class MobileNotificationListView(generics.ListAPIView):
    """
    GET list of my notification
    """
    serializer_class = MobileNotificationSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserNotificationPagination

    def get_queryset(self):
        queryset = MobileNotification.objects.filter(recipient=self.request.user).order_by("-created_at")
        return queryset
    
    
class MobileNotificationUpdateView(generics.UpdateAPIView):
    """
    Patch message update status read and unread in mobile notification
    """
    serializer_class = MobileNotificationUpdateSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = MobileNotification.objects.filter(recipient=self.request.user)
        return queryset
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
class MobileNotificationDetailView(generics.RetrieveAPIView):
    """
    Get message detail
    """
    serializer_class = MobileNotificationSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        queryset = MobileNotification.objects.filter(recipient=self.request.user)
        return queryset