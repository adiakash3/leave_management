from django.utils import timezone
from django.shortcuts import get_object_or_404
from emails.utils.emails import BaseEmail
from helpers.pagination import CustomPageNumberPagination
import datetime
from helpers.calculate_leave import *
from holidays.models import *

from rest_framework import generics
from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .serializers import *
from shifts.models import *


import logging
logger = logging.getLogger(__name__)


class MyLeavesList(generics.ListAPIView):
    """
    My Leaves created list with thier status
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveListSerializer
    pagination_class = CustomPageNumberPagination
    filterset_fields = ['leave_type__name', 'status', 'leave__status']
    
    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            return Leave.objects.filter(applied_by=self.request.user.employee, start_date_at__gte=start_date,
                                        start_date_at__lte=end_date).order_by('-created_at')
        else:
            return Leave.objects.filter(applied_by=self.request.user.employee).order_by('-created_at')

    
class LeaveDetailView(generics.RetrieveAPIView):
    """
    Retrive my leave details
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveListSerializer
    
    def get_queryset(self):
        queryset = Leave.objects.filter(applied_by=self.request.user.employee)
        return queryset
    
    
class GlobalLeavesTypesList(generics.ListAPIView):
    """
    Available all leaves types
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveTypeListSerializer
    pagination_class = CustomPageNumberPagination
    queryset = LeaveType.objects.all().order_by('id')


class MyUnauthorizedLeaveList(APIView):
    """
    My Unauthorized Leave List
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request, format=None):
        start_date = self.request.query_params.get('start_date','2020-04-01')
        end_date = self.request.query_params.get('end_date',datetime.datetime.today().strftime('%Y-%m-%d'))
        date_format = "%Y-%m-%d"
        start_date = datetime.datetime.strptime(start_date, date_format)
        end_date = datetime.datetime.strptime(end_date, date_format)
        total_days = (end_date-start_date).days + 1
        for day_number in range(total_days):
            current_date = start_date + datetime.timedelta(days=day_number)
            if not EmployeeShift.objects.filter(employee__user=self.request.user, start_date=current_date).exists():
                queryset = Leave.objects.filter(applied_by=self.request.user.employee).exclude(leave__status=LeaveStatus.APPROVED, ).order_by('-created_at')
                if not HolidayCalendar.objects.filter(holiday_on=current_date).exists():
                    serializer = UnauthorizedLeaveListSerializer(queryset, many=True)
                    return Response(serializer.data)
            elif EmployeeShift.objects.filter(employee__user=self.request.user, start_date=current_date).exists():
                for each in EmployeeShift.objects.filter(employee__user=self.request.user, start_date=current_date):
                    if each.employee_attendance == None:
                        queryset = Leave.objects.filter(applied_by=self.request.user.employee).exclude(leave__status=LeaveStatus.APPROVED, ).order_by('-created_at')
                        if not HolidayCalendar.objects.filter(holiday_on=current_date).exists():
                            serializer = UnauthorizedLeaveListSerializer(queryset, many=True)
                            return Response(serializer.data)



@api_view(['GET',])
@permission_classes([permissions.IsAuthenticated])
def my_leave_overview(request):
    """ show the details of my leave types with available and taken, carried"""
    now = timezone.now()
    next_year = now.year + 1
    if request.query_params.get('fy'):
        fy = request.query_params.get('fy')
        current_fy = get_object_or_404(FinancialYear, id=fy)
    else:
        current_fy = FinancialYear.objects.filter(start_date__year__gte=now.year, end_date__year__lte=next_year).first()
    current_fy_leave_config = get_object_or_404(FinancialYearLeaveConfig, id=current_fy.id)
    emp = Employee.objects.get(user=request.user)
    applied_by = models.ForeignKey(Employee, related_name='my_leaves', on_delete=models.CASCADE)
    leave_overview = []
    for leave_type in LeaveType.objects.all():
        taken = my_leave_count_based_on_type(emp, current_fy.start_date, current_fy.end_date, leave_type)
        pending_leave_count = Leave.objects.filter(applied_by=request.user.employee,leave_type=leave_type, leave__status=LeaveStatus.APPLIED).count()
        emp_fyl, _ = EmployeeFYL.objects.get_or_create(employee=emp, fy_leave_config=current_fy_leave_config, leave_type=leave_type)
        leave_overview.append({
            "leave_type": LeaveTypeListSerializer(leave_type).data,
            "total": leave_type.days,
            "taken": taken,
            "remaining": abs(taken - leave_type.days),
            "carried": emp_fyl.carried_leave_no,
            "leave_in_process":pending_leave_count
        })

    return Response(leave_overview)


class AppliedQueueLeaveListView(generics.ListAPIView):
    """
    Applied leaves for TL & Manager login using LeaveStatus model
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveStatusSerializer
    pagination_class = CustomPageNumberPagination
    filterset_fields = ['leave__leave_type__name', 'status', 'leave__status']

    def get_queryset(self):
        print(self.request.user)
        return LeaveStatus.objects.filter(approver=self.request.user,leave__status=Leave.APPLIED).order_by('-created_at')


class LeaveQueueDetailView(generics.RetrieveAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaveListSerializer

    def get_queryset(self):
        return Leave.objects.all()


class LeaveQueueApproveView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Leave.objects.get(pk=pk)
        except Leave.DoesNotExist:
            Response({'result': "Given id Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        leave_obj = self.get_object(pk)
        leave_obj.status = Leave.APPLIED
        leave_obj.save()
        leave_status_obj, _ = LeaveStatus.objects.get_or_create(leave=leave_obj)
        leave_status_obj.status = self.request.data['status']
        leave_status_obj.comments = self.request.data['comments']
        leave_status_obj.approver = request.user
        leave_status_obj.approver_action_at = timezone.now()
        leave_status_obj.save()
        return Response({'message': "success"}, status=status.HTTP_200_OK)


@api_view(['GET',])
@permission_classes([permissions.AllowAny])
def financial_years(request):
    """ available financial_years """
    fy = FinancialYear.objects.all()
    fys = FinancialYearSerializer(fy, many=True)
    return Response(fys.data)


@api_view(['POST',])
@permission_classes([permissions.IsAuthenticated])
def apply_leave(request):
    try:
        leave = Leave()
        leave.status = Leave.APPLIED
        leave.applied_by = request.user.employee
        leave.applied_on = timezone.now()
        leave.leave_type_id = request.POST['leave_type_id']
        leave.reason = request.POST['reason']
        leave.description = request.POST['description']
        leave.start_date_at = request.POST['start_date_at']
        leave.end_date_at = request.POST['end_date_at']
        leave.is_half_day = request.POST['is_half_day']
        leave.save()
        leave_status_obj, _ = LeaveStatus.objects.get_or_create(leave=leave)
        leave_status_obj.status = LeaveStatus.APPLIED
        leave_status_obj.approver = leave.applied_by.report_to
        leave_status_obj.save()
        return Response({'message': 'Leave applied successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("unable to create leave {}".format(e))
        return Response({'detail': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET',])
@permission_classes([permissions.AllowAny])
def leave_status_list(request):
    """ available leave status """
    leave_status = LeaveStatus.LEAVE_STATUS
    return Response({'leave_status':leave_status})
