from django.conf import settings
from django.db import models
from user_type_apps.employees.models import Employee
import datetime

class LeaveType(models.Model):
    """ Main leaves type and thier total days"""
    name = models.CharField(max_length=100)
    days = models.IntegerField()
    
    def __str__(self):
        return self.name + ' has total ' + str(self.days)
    
    
class Leave(models.Model):
    """
    Every one can apply for leave here
    when leave saved immediatly create or update the status
    """
    APPLIED = 'applied'
    UNAUTHORIZED = 'unauthorized'
    STATUS_CHOICES = (
        (APPLIED, 'Applied'),
        (UNAUTHORIZED, 'Unauthorized'),
    )
    applied_by = models.ForeignKey(Employee, related_name='my_leaves', on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    reason = models.TextField()
    description =  models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, blank=True, null=True)
    start_date_at = models.DateTimeField()
    end_date_at = models.DateTimeField()
    is_half_day = models.BooleanField(default=False)
    applied_on = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def total_days(self):
        "Returns the day diff between start_date_at and end_date_at"
        return (self.end_date_at - self.start_date_at).days + 1
        
    def __str__(self):
        return str(self.applied_by) + ' '+str(self.leave_type.name)
    
    
class LeaveStatus(models.Model):
    """Everyone leave status by heigher authorities"""
    APPROVED = 'approved'
    REJECTED = 'rejected'
    APPLIED = 'applied'
    
    LEAVE_STATUS = (
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (APPLIED, 'Applied'),
    )
    leave = models.OneToOneField(Leave, related_name='leave', on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=LEAVE_STATUS, default=APPLIED)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    approver_action_at = models.DateTimeField(blank=True, null=True)
    comments =  models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.leave) + str(self.status)
    
    
class FinancialYear(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def is_active(self):
        current_date = datetime.datetime.today().date()
        if self.start_date <= current_date <= self.end_date:
            is_active = True
        else:
            is_active = False
        return is_active

    def __str__(self):
        return "{} - {}".format(self.start_date.strftime('%d/%m/%Y'), self.end_date.strftime('%d/%m/%Y'))



class FinancialYearLeaveConfig(models.Model):
    financial_year = models.OneToOneField(FinancialYear, on_delete=models.CASCADE, related_name="leave_config")
    max_leave_carry = models.IntegerField(default=0)
    
    def __str__(self):
        return "{} {}".format(self.financial_year, self.max_leave_carry)


class EmployeeFYL(models.Model):
    fy_leave_config = models.ForeignKey(FinancialYearLeaveConfig, on_delete=models.CASCADE, related_name="leave_config")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employee_leave_fyl")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    carried_leave_no = models.IntegerField(default=0)
    comment = models.TextField()
    
    def __str__(self):
        return "{} {} {} {}".format(self.fy_leave_config, self.employee, self.leave_type, self.carried_leave_no)
