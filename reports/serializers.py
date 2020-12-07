from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from shifts.models import *

User = get_user_model()


class EmployeeOverTimeSerializer(serializers.ModelSerializer):
    attendance = serializers.SerializerMethodField()
    productivity_hours = serializers.SerializerMethodField()
    total_shift_hours = serializers.SerializerMethodField()
    time_worked = serializers.SerializerMethodField()
    overtime_worked = serializers.SerializerMethodField()
    
    def get_productivity_hours(self, obj):
        return str(obj.productivity_hours())

    def get_attendance(self, obj):
        if obj.employee_attendance:
            return "Present"
        return 'Absent'
    
    def get_total_shift_hours(self, obj):
        time_worked = str(obj.shift.total_shift_hours())
        return time_worked

    def get_time_worked(self, obj):
        if hasattr(obj.employee_attendance, 'time_worked'):
            time_worked = str(obj.employee_attendance.time_worked())
            return time_worked
        return "00:00:00"

    def get_overtime_worked(self, obj):
        total_shift_hours = obj.shift.total_shift_hours()
        if hasattr(obj.employee_attendance, 'time_worked'):
            time_worked = obj.employee_attendance.time_worked()
            if total_shift_hours >= time_worked:
                over_time = "00:00:00"
            else:
                over_time = str(time_worked - total_shift_hours)
            return over_time
        return "00:00:00"

    class Meta:
        model = EmployeeShift
        fields = ['attendance', 'shift','employee_attendance','time_worked','total_shift_hours','overtime_worked','start_date', 'end_date', 'productivity_hours']
        depth = 1