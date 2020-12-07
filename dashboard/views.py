from accounts.models import *
from departments.models import *
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from leaves.models import *
from shifts.models import *
from user_type_apps.managers.models import *
from user_type_apps.team_leaders.models import *
from user_type_apps.employees.models import *




@login_required
def index(request):
    now = timezone.now()

    # total TeamLeader,Manager,Department
    total_teamleader =TeamLeader.objects.count()
    total_manager =Manager.objects.count()
    total_departments = Department.objects.all().count()

    # this day
    total_leave_today = Leave.objects.filter(leave__status=LeaveStatus.APPROVED,start_date_at__lte=now.date(), end_date_at__gte=now.date()).count()
    total_unauthorized_leave_today = Leave.objects.filter(start_date_at__lte=now.date(), end_date_at__gte=now.date(),
                                                          status=Leave.UNAUTHORIZED).count()
    total_pending_leave_today = Leave.objects.filter(start_date_at__lte=now.date(), end_date_at__gte=now.date(),
                                                     leave__status=LeaveStatus.APPLIED).count()

    # this week
    week_start = now - datetime.timedelta(days=now.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    total_leave_week = Leave.objects.filter(leave__status=LeaveStatus.APPROVED,start_date_at__gte=week_start, end_date_at__lte=week_end).count()
    total_unauthorized_leave_week = Leave.objects.filter(start_date_at__gte=week_start, end_date_at__lte=week_end,
                                                         status=Leave.UNAUTHORIZED).count()
    total_pending_leave_week = Leave.objects.filter(start_date_at__gte=week_start, end_date_at__lte=week_end,
                                                    leave__status=LeaveStatus.APPLIED).count()

    # this month
    total_leave_month = Leave.objects.filter(start_date_at__month=now.month).count()
    total_unauthorized_leave_month = Leave.objects.filter(start_date_at__month=now.month,
                                                         status=Leave.UNAUTHORIZED).count()
    total_pending_leave_month = Leave.objects.filter(start_date_at__month=now.month,
                                                     leave__status=LeaveStatus.APPLIED).count()

    # total shift
    total_shift = Shift.objects.all().count()

    context = {}
    context['total_leave_week'] = total_leave_week
    context['total_unauthorized_leave_week'] = total_unauthorized_leave_week
    context['total_pending_leave_week'] = total_pending_leave_week
    context['total_leave_today'] = total_leave_today
    context['total_unauthorized_leave_today'] = total_unauthorized_leave_today
    context['total_pending_leave_today'] = total_pending_leave_today
    context['total_leave_month'] = total_leave_month
    context['total_unauthorized_leave_month'] = total_unauthorized_leave_month
    context['total_pending_leave_month'] = total_pending_leave_month
    context['total_shift'] = total_shift
    context['total_teamleader'] = total_teamleader
    context['total_manager'] = total_manager
    context['total_departments'] = total_departments
    return render(request, 'dashboard/home.html', context)