from emails.utils.emails import BaseEmail
from helpers.pagination import CustomPageNumberPagination,OvertimePagination
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework import authentication, permissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.utils import timezone
from .serializers import *
import datetime
import logging
from django.shortcuts import get_object_or_404
logger = logging.getLogger(__name__)



class MyAttendanceList(generics.ListAPIView):
    """
    My Leaves Attendance List with week & month scenario
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MyAttendanceListSerializer
    pagination_class = OvertimePagination
    
    def last_day_of_month(self, any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def get_queryset(self):
        start_week = timezone.now() - datetime.timedelta(timezone.now().weekday())
        end_week = start_week + datetime.timedelta(6)
        start_of_month = timezone.now().replace(day=1).date()
        end_of_month = self.last_day_of_month(start_of_month)
        day_type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if day_type == 'weekly':
            return EmployeeShift.objects.filter(employee__user=self.request.user).filter(start_date__gte=start_week.date(),end_date__lte=end_week.date()).order_by('-created_at')
        elif day_type == 'monthly':
            return EmployeeShift.objects.filter(employee__user=self.request.user).filter(start_date__gte=start_of_month,end_date__lte=end_of_month).order_by('-created_at')
        elif start_date and end_date:
            return EmployeeShift.objects.filter(employee__user=self.request.user).filter(start_date__gte=start_date,start_date__lte=end_date).order_by('-created_at')
        else:
            return EmployeeShift.objects.filter(employee__user=self.request.user).all().order_by('-created_at')


class MyShiftListView(generics.ListAPIView):
    """
    GET employee shift List with weekly or monthly
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmployeeShiftSerializer
    pagination_class = CustomPageNumberPagination
    
    def last_day_of_month(self, any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def get_queryset(self):
        shift_type = self.request.query_params.get('shift_type')
        p_start_date = self.request.query_params.get('start_date')
        p_end_date = self.request.query_params.get('end_date')
            
        start_week = timezone.now() - datetime.timedelta(timezone.now().weekday())
        end_week = start_week + datetime.timedelta(6)
        start_of_month = timezone.now().replace(day=1).date()
        end_of_month = self.last_day_of_month(start_of_month)
        
        employee_shift_qs = EmployeeShift.objects.filter(employee__user=self.request.user).order_by('start_date')
        if p_start_date and p_end_date:
            return employee_shift_qs.filter(start_date__gte=p_start_date, start_date__lte=p_end_date)
        elif shift_type == 'this_week':
            return employee_shift_qs.filter(start_date__gte=start_week.date(), end_date__lte=end_week.date())
        elif shift_type == 'this_month':
            return employee_shift_qs.filter(start_date__gte=start_of_month, end_date__lte=end_of_month)
        else:
            return employee_shift_qs


class LateExemptsQueueListView(generics.ListAPIView):
    """
    TL or manager will have the queue of employee applied late exempte 
    later tl can approve
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MyApproveOnLateExemptSerializer
    pagination_class = CustomPageNumberPagination
    filterset_fields = ['status']

    def get_queryset(self):
        return LateExemptStatus.objects.filter(report_to__user=self.request.user).order_by('-created_at')
     
        
class LateExemptsQueueDetailView(generics.RetrieveUpdateAPIView):
    """
    TL or manager will can see the detail of the employee applied late exempte 
    here tl or manager can approve
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MyApproveOnLateExemptSerializer
        return MyApproveOnLateExemptUpdateSerializer

    def get_queryset(self):
        return LateExemptStatus.objects.filter(report_to__user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(action_by=self.request.user.employee, action_at=timezone.now())
        
        
@api_view(['POST',])
@permission_classes([permissions.IsAuthenticated])
def apply_late_exempt(request):
    """
    all employee can apply for late exempt from front end 
    using employee shift mapping id
    """
    try:
        late_exempt = LateExempt()
        late_exempt.employee_shift_id = request.POST['employee_shift_id']
        late_exempt.late_type = request.POST['late_type']
        late_exempt.check_in = request.POST.get('check_in')
        late_exempt.check_out = request.POST.get('check_out')
        late_exempt.comment = request.POST['comment']
        late_exempt.save()
        
        late_exempt_status_obj, _ = LateExemptStatus.objects.get_or_create(late_exempt=late_exempt)
        late_exempt_status_obj.status = LateExemptStatus.RECEIVED
        late_exempt_status_obj.report_to = get_object_or_404(Employee, user= request.user.employee.report_to)
        late_exempt_status_obj.save()
        return Response({'message': 'Applied successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("unable to apply late exempt {}".format(e))
        return Response({'detail': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)


class AppliedLateExemptDetails(generics.RetrieveAPIView):
    """
    employee can view his own late exempt details
    """
    serializer_class = LateExemptSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return LateExempt.objects.filter(employee_shift__employee__user=self.request.user)
    
    
class AppliedLateExemptListView(generics.ListAPIView):
    """
    My Applied late exempts list
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LateExemptStatusSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return LateExemptStatus.objects.filter(late_exempt__employee_shift__employee__user=self.request.user).all().order_by('-created_at')
