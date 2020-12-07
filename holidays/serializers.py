from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class HolidaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HolidayCalendar
        fields = "__all__"