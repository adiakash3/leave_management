from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from .models import *

User = get_user_model()


class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Break
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    breaks = BreakSerializer(many=True)

    class Meta:
        model = Shift
        fields = ['name','code', 'start_time','end_time','breaks']


class MyAttendanceListSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee_attendance.employee.user.first_name', read_only=True)
    check_in = serializers.ReadOnlyField(source='employee_attendance.check_in', read_only=True)
    check_out = serializers.ReadOnlyField(source='employee_attendance.check_out', read_only=True)
    date = serializers.ReadOnlyField(source='employee_attendance.date', read_only=True)
    shift = ShiftSerializer()
    time_worked = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeShift
        fields = ['start_date','end_date','employee_name','check_in','check_out','date','shift','time_worked']
        
    def get_time_worked(self, obj):
        if obj.employee_attendance:
            return str(obj.employee_attendance.time_worked())
        return "00:00:00"
    
class AttendanceSerializer(serializers.ModelSerializer):    
    class Meta:
        model = EmployeeAttendance
        fields = "__all__"
        

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
        
class EmployeeSerializer(serializers.ModelSerializer):
    
    user = UserSerializer()    
    class Meta:
        model = Employee
        fields = "__all__"
            
class EmployeeShiftSerializer(serializers.ModelSerializer):
    shift = ShiftSerializer()
    employee = EmployeeSerializer()
    employee_attendance = AttendanceSerializer()
    
    class Meta:
        model = EmployeeShift
        fields = "__all__"


class LateExemptSerializer(serializers.ModelSerializer):
    employee_shift = EmployeeShiftSerializer()
    class Meta:
        model = LateExempt
        fields = "__all__"
        
        
class MyApproveOnLateExemptSerializer(serializers.ModelSerializer):
    late_exempt = LateExemptSerializer()
    
    class Meta:
        model = LateExemptStatus
        exclude = ('report_to',)
        
    
class MyApproveOnLateExemptUpdateSerializer(serializers.ModelSerializer):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    RECEIVED = 'received'
    STATUS_CHOICES = (
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (RECEIVED, 'Received'),
    )
    comment = serializers.CharField()    
    status = serializers.ChoiceField(choices=STATUS_CHOICES)  
    class Meta:
        model = LateExemptStatus
        fields = ('status', 'comment')
        
        
class LateExemptStatusSerializer(serializers.ModelSerializer):
    late_exempt = LateExemptSerializer()
    report_to = EmployeeSerializer()
    class Meta:
        model = LateExemptStatus
        fields = "__all__"
