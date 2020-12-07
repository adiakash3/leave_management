from django.utils import timezone
from emails.utils.emails import BaseEmail
from rest_framework import generics
from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .serializers import *

import logging
logger = logging.getLogger(__name__)

class HolidayListView(generics.ListAPIView):
    """
    Holidays list
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HolidaySerializer
    
    def get_queryset(self):
        queryset = HolidayCalendar.objects.filter(holiday_on__year=timezone.now().year)
        return queryset.order_by('holiday_on')