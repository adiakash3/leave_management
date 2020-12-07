from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from .models import *
from datetime import date, timedelta
User = get_user_model()

class LeaveTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"
        
        
class LeaveListSerializer(serializers.ModelSerializer):
    leave_type =  serializers.SerializerMethodField()
    leave_status = serializers.SerializerMethodField()

    class Meta:
        model = Leave
        fields = "__all__"
        
    def get_leave_type(self, obj):
        return obj.leave_type.name
    
    def get_leave_status(self, obj):
        if hasattr(obj, 'leave'):
            return LeaveStatusSerializer(obj.leave).data 
        else:
            return None


class LeaveStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveStatus
        fields = "__all__"
        depth = 3
        
class UnauthorizedLeaveListSerializer(serializers.ModelSerializer):
    no_of_leave_days_taken = serializers.SerializerMethodField()
    leave_dates = serializers.SerializerMethodField()


    class Meta:
        model = Leave
        fields = ['no_of_leave_days_taken','leave_dates']

    def get_no_of_leave_days_taken(self, obj):
        if obj.is_half_day == True:
            return (obj.end_date_at - obj.start_date_at).days + 0.5
        else:
            return (obj.end_date_at - obj.start_date_at).days + 1

    def get_leave_dates(self, obj):
        sdate = obj.start_date_at
        edate = obj.end_date_at
        leave_dates = []
        if obj.is_half_day == True:
            leave_dates.append({'date': sdate,
                    'is_half_day': obj.is_half_day})
        else:
            leave_dates.append({'date': sdate,'is_half_day': obj.is_half_day})
        delta = edate - sdate
        obj.is_half_day = False
        for i in range(delta.days):
            days = sdate + timedelta(days=1) + timedelta(days=i)
            leave_dates.append({'date': days,'is_half_day:': obj.is_half_day})

        return leave_dates

    def get_applied_by(self,obj):
        return obj.applied_by.user.first_name




class FinancialYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialYear
        fields = ['id','start_date','end_date','is_active']