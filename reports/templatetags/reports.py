from django import template
from django.db.models import Q
from django.utils import timezone
from leaves.models import EmployeeFYL, Leave, LeaveStatus, LeaveType
from shifts.models import EmployeeShift
from holidays.models import HolidayCalendar
import datetime
register = template.Library() 

@register.filter(name='find_my_this_day_shift') 
def find_my_this_day_shift(employee, today_date):
    try:
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        return employee_shift_map.shift.name
    except Exception as e:
        return "N/A"

@register.filter(name='find_my_this_day_shift_code')
def find_my_this_day_shift_code(employee, today_date):
    try:
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        return employee_shift_map.shift.code
    except Exception as e:
        return "N/A"

@register.filter(name='find_my_this_day_late')
def find_my_this_day_late(employee, today_date):
    try:
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        shift_start_time = datetime.datetime.strptime(str(employee_shift_map.shift.start_time), '%H:%M:%S')
        check_in_time = datetime.datetime.strptime(str(employee_shift_map.employee_attendance.check_in), '%H:%M:%S')
        if check_in_time <= shift_start_time:
            return "00:00:00"
        late_by = check_in_time - shift_start_time
        return late_by
    except Exception as e:
        return "N/A"

@register.filter(name='find_my_this_day_early')
def find_my_this_day_early(employee, today_date):
    try:
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        shift_end_time = datetime.datetime.strptime(str(employee_shift_map.shift.end_time), '%H:%M:%S')
        check_out_time = datetime.datetime.strptime(str(employee_shift_map.employee_attendance.check_out), '%H:%M:%S')
        if check_out_time >= shift_end_time:
            return "00:00:00"
        early_by = shift_end_time - check_out_time
        return early_by
    except Exception as e:
        return "N/A"
    

@register.filter(name='find_my_this_day_check_in') 
def find_my_this_day_check_in(employee, today_date):
    try:
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        return employee_shift_map.employee_attendance.check_in
    except Exception as e:
        return "N/A"

@register.filter(name='find_my_this_day_check_out') 
def find_my_this_day_check_out(employee, today_date):
    try:
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        return employee_shift_map.employee_attendance.check_out
    except Exception as e:
        return "N/A"

@register.filter(name='find_my_this_day_time_worked') 
def find_my_this_day_time_worked(employee, today_date):
    try:
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        return employee_shift_map.employee_attendance.time_worked()
    except Exception as e:
        return "N/A"
    
    
@register.filter(name='am_i_present') 
def am_i_present(employee, today_date):
    try:
        if today_date > timezone.now().date():
            return 'N/A'
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        employee_shift_map.employee_attendance.check_in
        return "P"
    except Exception as e:
        return "A"
    
    
@register.filter(name='my_overtime_worked') 
def my_overtime_worked(employee, today_date):
    try:
        if today_date > timezone.now().date():
            return 'N/A'
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        total_shift_hours = employee_shift_map.shift.total_shift_hours()
        time_worked = employee_shift_map.employee_attendance.time_worked()
        print(total_shift_hours)
        print(time_worked)
        if total_shift_hours >= time_worked:
            return "00:00:00"
        else:
            return time_worked - total_shift_hours
    except Exception as e:
        return "N/A"
    
    
@register.filter(name='my_less_time_worked') 
def my_less_time_worked(employee, today_date):
    try:
        if today_date > timezone.now().date():
            return 'N/A'
        employee_shift_map = EmployeeShift.objects.get(employee=employee, start_date=today_date)
        total_shift_hours = employee_shift_map.shift.total_shift_hours()
        time_worked = employee_shift_map.employee_attendance.time_worked()
        print(total_shift_hours)
        print(time_worked)
        if total_shift_hours <= time_worked:
            return "00:00:00"
        else:
            return total_shift_hours - time_worked
    except Exception as e:
        return "N/A"
    
    
@register.simple_tag 
def my_leave_count(employee, start_date, end_date):
    """
    Employee total approved leaves.
    while applying future leave only full days leaves.
    emp coming to office late or going early only half days leave.
    1. first collect offically approved leaves btw these days with half day considere
    2. then collect unauthorized leaves(TODO)
    """
    try:
        holiday_count = 0
        for leave_type in LeaveType.objects.all():
            holiday_count += my_leave_count_based_on_type(employee, start_date, end_date, leave_type)
        
        print('offically approved leaves {} '.format(holiday_count))
        return holiday_count
    except Exception as e:
        return "N/A"
    
    
@register.simple_tag 
def my_leave_count_based_on_type(employee, p_start_date, p_end_date, leave_type):
    """ employee leave from start date to end date based on type"""
    try:
        holiday_count = 0
        total_days = (p_end_date - p_start_date).days + 1
        leave_took_qs = Leave.objects.filter(
                                            Q(start_date_at__date__range=(p_start_date,p_end_date)) |
                                            Q(end_date_at__date__range=(p_start_date,p_end_date)),
                                            applied_by=employee.user, leave__status=LeaveStatus.APPROVED,
                                            leave_type=leave_type,
        )
        for leave in leave_took_qs:
            is_first_time = leave.is_half_day
            for day_number in range(total_days):
                current_date = p_start_date + datetime.timedelta(days = day_number)
                if leave.start_date_at.date() <= current_date <= leave.end_date_at.date():
                    # in between
                    if is_first_time and leave.start_date_at.date() >= p_start_date:
                        holiday_count += 0.5
                        is_first_time = False
                    else:
                        holiday_count +=1
                    
        return holiday_count
    except Exception as e:
        return "N/A"
    
    
@register.simple_tag 
def my_unauthorized_leave_count(employee, start_date, end_date):
    """ employee leave from start date to end date based on type"""
    try:
        
        holiday_count = 0
        total_days = (end_date - start_date).days + 1
        for day_number in range(total_days):
            current_date = start_date + datetime.timedelta(days = day_number)
            if employee.created_at.date() <= current_date:
                # employee already registered
                if not EmployeeShift.objects.filter(employee=employee, start_date=current_date).exists():
                    # he is not went office
                    holiday_count +=1
                else:
                    # tl created his shift but he shift time checkin is later
                    emp_shift = EmployeeShift.objects.get(employee=employee, start_date=current_date)
                    # except current date check attendance
                    if current_date != timezone.now().date():
                        try:
                            emp_shift.employee_attendance.check_in
                        except Exception as e:
                            # he not came
                            holiday_count +=1
                        continue
                    # for today date check check shift timings
                    # shift time start at 11:00 am > now time is 10:00 am, 24format
                    if emp_shift.shift.start_time >= timezone.now().time():
                        # not a working time
                        continue
                    else:
                        # shift started
                        # check his attendance checkin
                        # required validate
                        try:
                            emp_shift.employee_attendance.check_in
                        except Exception as e:
                            # he not came
                            holiday_count +=1
        return holiday_count
    except Exception as e:
        return "N/A"


@register.simple_tag
def my_unauthorized_leave(employee, p_start_date, p_end_date):
    """
    Employee unauthorized leave :
    leave status not approved,
    Employee shift doesn't exist, no holiday
    """
    try:
        holiday_count = 0
        total_days = (p_end_date - p_start_date).days + 1
        for day_number in range(total_days):
            current_date = p_start_date + datetime.timedelta(days=day_number)
            # if employee shift is present but  employee attendance is absent
            if EmployeeShift.objects.filter(employee=employee, start_date=current_date).exists():
                for each in EmployeeShift.objects.filter(employee=employee, start_date=current_date):
                    if each.employee_attendance == None:
                        # check in leave(table) approved or not
                        leave_took_qs = Leave.objects.filter(
                            Q(start_date_at__date__range=(p_start_date, p_end_date)) |
                            Q(end_date_at__date__range=(p_start_date, p_end_date)),
                            applied_by=employee.user).exclude(leave__status=LeaveStatus.APPROVED, )
                        # check current day is holiday or not in holiday table
                        if not HolidayCalendar.objects.filter(holiday_on=current_date).exists():
                            for leave in leave_took_qs:
                                if leave.start_date_at.date() <= current_date <= leave.end_date_at.date():
                                    holiday_count += 1
                #if Employee_shift is not present
            elif not EmployeeShift.objects.filter(employee=employee, start_date=current_date).exists():
                # check in leave(table) approved or not
                leave_took_qs = Leave.objects.filter(
                    Q(start_date_at__date__range=(p_start_date, p_end_date)) |
                    Q(end_date_at__date__range=(p_start_date, p_end_date)),
                    applied_by=employee.user).exclude(leave__status=LeaveStatus.APPROVED,)
                # check current day is holiday or not in holiday table
                if not HolidayCalendar.objects.filter(holiday_on=current_date).exists():
                    for leave in leave_took_qs:
                        if leave.start_date_at.date() <= current_date <= leave.end_date_at.date():
                            holiday_count += 1

        return holiday_count
    except Exception as e:
        return "N/A"
    
    
@register.simple_tag 
def my_carry_leave_count_based_on_leave_type(employee, leave_config, leave_type):
    try:
        emp_fyl = EmployeeFYL.objects.get(employee=employee, fy_leave_config=leave_config, leave_type=leave_type)
        return emp_fyl.carried_leave_no
    except EmployeeFYL.DoesNotExist:
        return 0
    
    
@register.filter(name='my_duration_worked_for_given_month') 
def my_duration_worked_for_given_month(employee, today_date):
    try:
        employee_shift_maps = EmployeeShift.objects.filter(employee=employee,start_date__year=today_date.year, start_date__month=today_date.month)
        today_all_worked_hours = datetime.timedelta(0)
        for employee_shift_map in employee_shift_maps:
            if employee_shift_map.employee_attendance:
                today_all_worked_hours += employee_shift_map.employee_attendance.time_worked()
        
        totsec = int(today_all_worked_hours.total_seconds())
        if totsec == 0:
            today_all_worked_hours = {
                'h':  0,
                'm': 0,
                'sec':0,
            }
        else:
            h = totsec//3600
            m = (totsec%3600) // 60
            sec = (totsec%3600)%60
            if h < 10:
                h = "0{}".format(h)
            if m < 10:
                m = "0{}".format(m)
            if sec < 10:
                m = "0{}".format(sec)
            today_all_worked_hours = {
                
                'h':  h,
                'm': m,
                'sec':sec,
            }
        return "{}:{}:{}".format(today_all_worked_hours['h'],today_all_worked_hours['m'],today_all_worked_hours['sec'],)
    except Exception as e:
        return "00:00:00"
    
    
@register.filter(name='my_overtime_worked_for_given_month') 
def my_overtime_worked_for_given_month(employee, today_date):
    try:
        employee_shift_maps = EmployeeShift.objects.filter(employee=employee,start_date__year=today_date.year, start_date__month=today_date.month)
        total_extra_worked_hours = datetime.timedelta(0)
        for employee_shift_map in employee_shift_maps:
            if employee_shift_map.employee_attendance:
                shift_total_hours = employee_shift_map.shift.total_shift_hours()
                time_worked = employee_shift_map.employee_attendance.time_worked()
                if time_worked > shift_total_hours:
                    total_extra_worked_hours += time_worked - shift_total_hours
        
        totsec = int(total_extra_worked_hours.total_seconds())
        if totsec == 0:
            total_extra_worked_hours = {
                'h':  0,
                'm': 0,
                'sec':0,
            }
        else:
            h = totsec//3600
            m = (totsec%3600) // 60
            sec = (totsec%3600)%60
            if h < 10:
                h = "0{}".format(h)
            if m < 10:
                m = "0{}".format(m)
            if sec < 10:
                m = "0{}".format(sec)
            total_extra_worked_hours = {
                
                'h':  h,
                'm': m,
                'sec':sec,
            }
        return "{}:{}:{}".format(total_extra_worked_hours['h'],total_extra_worked_hours['m'],total_extra_worked_hours['sec'],)
    except Exception as e:
        return "00:00:00"
    

@register.filter(name='my_required_worked_for_given_month') 
def my_required_worked_for_given_month(employee, today_date):
    try:
        employee_shift_maps = EmployeeShift.objects.filter(employee=employee,start_date__year=today_date.year, start_date__month=today_date.month)
        total_extra_worked_hours = datetime.timedelta(0)
        for employee_shift_map in employee_shift_maps:
            if employee_shift_map.employee_attendance:
                shift_total_hours = employee_shift_map.shift.total_shift_hours()
                time_worked = employee_shift_map.employee_attendance.time_worked()
                if time_worked < shift_total_hours:
                    total_extra_worked_hours +=  shift_total_hours - time_worked
        
        totsec = int(total_extra_worked_hours.total_seconds())
        if totsec == 0:
            total_extra_worked_hours = {
                'h':  0,
                'm': 0,
                'sec':0,
            }
        else:
            h = totsec//3600
            m = (totsec%3600) // 60
            sec = (totsec%3600)%60
            if h < 10:
                h = "0{}".format(h)
            if m < 10:
                m = "0{}".format(m)
            if sec < 10:
                m = "0{}".format(sec)
            total_extra_worked_hours = {
                
                'h':  h,
                'm': m,
                'sec':sec,
            }
        return "{}:{}:{}".format(total_extra_worked_hours['h'],total_extra_worked_hours['m'],total_extra_worked_hours['sec'],)
    except Exception as e:
        return "00:00:00"
    

@register.filter(name='my_productive_hours_worked_for_given_month') 
def my_productive_hours_worked_for_given_month(employee, today_date):
    try:
        employee_shift_maps = EmployeeShift.objects.filter(employee=employee,start_date__year=today_date.year, start_date__month=today_date.month)
        today_all_worked_hours = datetime.timedelta(0)
        shift_break_intervals = datetime.timedelta(0)
        for employee_shift_map in employee_shift_maps:
            if employee_shift_map.employee_attendance:
                
                for shift_break in employee_shift_map.shift.breaks.all():
                    if shift_break.start_time > shift_break.end_time:
                        start_date = datetime.datetime.combine(datetime.date.today(), shift_break.start_time)
                        end_date = datetime.datetime.combine(datetime.date.today()+datetime.timedelta(days=1), shift_break.end_time)
                        interval = end_date - start_date
                        shift_break_intervals += interval
                    else:
                        interval = datetime.datetime.combine(datetime.date.today(), shift_break.end_time) - datetime.datetime.combine(datetime.date.today(), shift_break.start_time)
                        shift_break_intervals += interval
                print("total break hours", shift_break_intervals)
                
                today_all_worked_hours += employee_shift_map.employee_attendance.time_worked()
               
        # exclude break
        today_all_worked_hours = int(today_all_worked_hours.total_seconds())
        shift_break_intervals = int(shift_break_intervals.total_seconds())
        # productivity
        totsec = today_all_worked_hours - shift_break_intervals
        if totsec == 0:
            total_productivity_hours = {
                'h':  0,
                'm': 0,
                'sec':0,
            }
        else:
            h = totsec//3600
            m = (totsec%3600) // 60
            sec = (totsec%3600)%60
            if h < 10:
                h = "0{}".format(h)
            if m < 10:
                m = "0{}".format(m)
            if sec < 10:
                m = "0{}".format(sec)
            total_productivity_hours = {
                
                'h':  h,
                'm': m,
                'sec':sec,
            }
        return "{}:{}:{}".format(total_productivity_hours['h'],total_productivity_hours['m'],total_productivity_hours['sec'],)
    except Exception as e:
        return "00:00:00"
    
    
@register.filter(name='my_no_of_days_worked_for_given_month') 
def my_no_of_days_worked_for_given_month(employee, today_date):
    try:
        employee_shift_maps = EmployeeShift.objects.filter(employee=employee,start_date__year=today_date.year, start_date__month=today_date.month)
        no_of_days_worked = 0
        for employee_shift_map in employee_shift_maps:
            if employee_shift_map.employee_attendance:
                no_of_days_worked += 1
            
        # Guaranteed to get the next month. Force any_date to 28th and then add 4 days.
        next_month = today_date.replace(day=28) + datetime.timedelta(days=4)
        
        # Subtract all days that are over since the start of the month.
        last_day_of_month = next_month - datetime.timedelta(days=next_month.day)
        return "{} / {}".format(no_of_days_worked,last_day_of_month.day)
    except Exception as e:
        return "{} / {}".format(0,last_day_of_month.day)
   