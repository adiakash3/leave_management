from django.db.models import Q
from leaves.models import Leave, LeaveStatus
import datetime

def my_leave_count_based_on_type(employee, p_start_date, p_end_date, leave_type):
    """ employee leave from start date to end date based on type"""
    try:
        holiday_count = 0
        total_days = (p_end_date - p_start_date).days + 1
        leave_took_qs = Leave.objects.filter(
                                            Q(start_date_at__date__range=(p_start_date,p_end_date)) |
                                            Q(end_date_at__date__range=(p_start_date,p_end_date)),
                                            applied_by=employee, leave__status=LeaveStatus.APPROVED,
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
  