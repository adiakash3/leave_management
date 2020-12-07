from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()


class FcmSetting(models.Model):
    """
    store fcm settings here
    """
    api_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class MobileDevice(models.Model):
    """
    Mobile types and thier fcm auth token
    """
    IOS = "ios"
    ANDROID = "android"
    
    DEVICE_TYPES = (
        (IOS, 'iOS'),
        (ANDROID, 'Android')
    )
    participant = models.OneToOneField(User, related_name='device', on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=DEVICE_TYPES)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.participant)


class MobileNotification(models.Model):
    UNREAD = "unread"
    READ = "read"
    
    MESSAGE_STATUS = (
        (UNREAD, 'Unread'),
        (READ, 'Read')
    )
    recipient = models.ForeignKey(User, related_name='user_device_notifications', on_delete=models.CASCADE)
    title = models.CharField(max_length=512, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=MESSAGE_STATUS, default=UNREAD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.recipient)