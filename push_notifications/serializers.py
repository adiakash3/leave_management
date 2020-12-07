from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model


class MobileDeviceReadSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()
    
    class Meta:
        model = MobileDevice
        fields = ["platform", "token"]
        
    def get_platform(self, obj):
        return obj.get_platform_display()


class MobileDeviceWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MobileDevice
        fields = ["platform", "token"]
    
    def update(self,instance, validated_data):
        instance.platform = validated_data['platform'].lower()
        instance.token = validated_data['token']
        instance.save()
        return instance
        


class MobileNotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MobileNotification
        exclude = ["recipient"]
        
        
class MobileNotificationUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MobileNotification
        fields = ["status"]