from helpers.pagination import *
from rest_framework import authentication, permissions
from rest_framework import generics
from shifts.models import *
from .serializers import *
import logging
logger = logging.getLogger(__name__)


class EmployeeOverTime(generics.ListAPIView):
    """
    Employee OverTime worked & in between dates
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmployeeOverTimeSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        start_date =  self.request.query_params.get('start_date')
        end_date =  self.request.query_params.get('end_date')
        if start_date and end_date:
            return EmployeeShift.objects.filter(employee__user=self.request.user,start_date__gte=start_date, start_date__lte=end_date).order_by('start_date')
        else:
            return EmployeeShift.objects.filter(employee__user=self.request.user).order_by('start_date')
