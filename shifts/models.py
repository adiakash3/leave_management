from django.db import models
from django.utils import timezone
from user_type_apps.employees.models import *
import datetime

class ModelDateCommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class Break(ModelDateCommonInfo):
    """ Break master """
    name = models.CharField(max_length=150)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return self.name
    
    
class Shift(ModelDateCommonInfo):
    """ Shift master """
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, null=True, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    breaks = models.ManyToManyField(Break, blank=True)
    
    def total_shift_hours(self):
        """ Total shift hours"""
        start_time = datetime.datetime.combine(self.created_at, self.start_time)
        if self.end_time <= self.start_time:
            next_day = self.created_at+datetime.timedelta(days=1)
        else:
            next_day = self.created_at
        end_time = datetime.datetime.combine(next_day, self.end_time)
        total_hours = end_time-start_time
        return total_hours
    
    def __str__(self):
        return self.name
    
    
class EmployeeAttendance(ModelDateCommonInfo):
    """ All employees attandance """
    employee = models.ForeignKey(Employee, related_name='employee_attendances', on_delete=models.CASCADE)
    check_in = models.TimeField()
    check_out = models.TimeField()
    date = models.DateTimeField()
    
    def time_worked(self):
        check_in = datetime.datetime.combine(self.date, self.check_in)
        if not self.check_out:
            time_working = timezone.now().time() - self.check_in
            return time_working
        if self.check_out <= self.check_in:
            next_day = self.date+datetime.timedelta(days=1)
        else:
            next_day = self.date
        check_out = datetime.datetime.combine(next_day, self.check_out)
        time_worked = check_out-check_in
        return time_worked
        
    
    def __str__(self):
        return 'emp {} checkin {} checkout {} on {}'.format(self.employee,
                                                            self.check_in,
                                                            self.check_out,
                                                            self.date)
    
    
class EmployeeShift(ModelDateCommonInfo):
    """ All employees shift maping """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    employee_attendance = models.ForeignKey(EmployeeAttendance, on_delete=models.CASCADE, blank=True, null=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    
    
    def productivity_hours(self):
        """remove break from time worked"""
        if not self.employee_attendance or not self.employee_attendance.check_out:
            return 'N/A'
        shift_break_intervals = datetime.timedelta(0)
        for shift_break in self.shift.breaks.all():
            if shift_break.start_time > shift_break.end_time:
                start_date = datetime.datetime.combine(datetime.date.today(), shift_break.start_time)
                end_date = datetime.datetime.combine(datetime.date.today()+datetime.timedelta(days=1), shift_break.end_time)
                interval = end_date - start_date
                shift_break_intervals += interval
            else:
                interval = datetime.datetime.combine(datetime.date.today(), shift_break.end_time) - datetime.datetime.combine(datetime.date.today(), shift_break.start_time)
                shift_break_intervals += interval
        print("total break hours", shift_break_intervals)
        
        full_time =  self.employee_attendance.time_worked()
        if shift_break_intervals >= full_time:
            # if more break than worked hour
            return '00:00:00'
        # exclude break
        productivity_time = full_time - shift_break_intervals
        print("productivity_time", productivity_time)
        
        return productivity_time

    def late_by(self):
        if not self.employee_attendance or not self.employee_attendance.check_in:
            return 'N/A'
        shift_start_time = datetime.datetime.strptime(str(self.shift.start_time),'%H:%M:%S')
        check_in_time = datetime.datetime.strptime(str(self.employee_attendance.check_in), '%H:%M:%S')
        if check_in_time <= shift_start_time:
            return "00:00:00"
        late_by = check_in_time - shift_start_time
        return late_by

    def early_by(self):
        if not self.employee_attendance or not self.employee_attendance.check_out:
            return 'N/A'
        shift_end_time = datetime.datetime.strptime(str(self.shift.end_time), '%H:%M:%S')
        check_out_time = datetime.datetime.strptime(str(self.employee_attendance.check_out), '%H:%M:%S')
        if check_out_time >= shift_end_time:
            return "00:00:00"
        early_by = shift_end_time - check_out_time
        return early_by


    def __str__(self):
        return "{} has {} shift on {}" .format(self.employee,self.shift, self.start_date)
    
    

class LateExempt(ModelDateCommonInfo):
    """store late coming to office and get approve"""
    LATE_COMING = "late_coming"
    EARLY_GOING = "early_going"
    LATE_TYPE_CHOICES = (
        (LATE_COMING, 'Late coming'),
        (EARLY_GOING, 'Early Going'),

    )
    employee_shift = models.OneToOneField(EmployeeShift, related_name='late_exempt', on_delete=models.CASCADE)
    check_in = models.TimeField(blank=True, null=True)
    late_coming = models.TimeField(blank=True, null=True)
    
    check_out = models.TimeField(blank=True, null=True)
    early_going = models.TimeField(blank=True, null=True)
    
    late_type = models.CharField(max_length=50, choices=LATE_TYPE_CHOICES, null=True)
    comment = models.TextField()
    
    def __str__(self):
        return str(self.employee_shift)
    
    
class LateExemptStatus(ModelDateCommonInfo):
    """ late coming to office and get approve"""
    APPROVED = 'approved'
    REJECTED = 'rejected'
    RECEIVED = 'received'
    STATUS_CHOICES = (
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (RECEIVED, 'Received'),
    )
    late_exempt = models.OneToOneField(LateExempt, related_name='late_exempt_status', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default=RECEIVED, max_length=25)
    report_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name="assigned_late_exempts", null=True)
    action_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name="action_done_late_exempts", blank=True, null=True)
    action_at = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return "{} has status {}".format(self.late_exempt, self.status)