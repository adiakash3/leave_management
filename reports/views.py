from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum
from django.shortcuts import render, HttpResponse, get_object_or_404 , HttpResponseRedirect, reverse
from django.utils import timezone
from helpers.web_paginators import get_fun_pagiantion
from leaves.models import *
from shifts.models import *
from .forms import *
import datetime
from django.contrib import messages
from user_type_apps.managers.models import *
from user_type_apps.team_leaders.models import *
from user_type_apps.employees.models import *
from departments.models import *

@login_required
def report_view(request):
    now = timezone.now()
    monday = now - datetime.timedelta(days = now.weekday())
    if request.GET.get('day'):
        day = int(request.GET.get('day'))
        if day == 1:
            which_date = monday.date()
        elif day == 2:
            which_date = (monday+datetime.timedelta(days=1)).date()
        elif day == 3:
            which_date = (monday+datetime.timedelta(days=2)).date()
        elif day == 4:
            which_date = (monday+datetime.timedelta(days=3)).date()
        elif day == 5:
            which_date = (monday+datetime.timedelta(days=4)).date()
        elif day == 6:
            which_date = (monday+datetime.timedelta(days=5)).date()
        elif day == 7:
            which_date = (monday+datetime.timedelta(days=6)).date()
        form = DaysForm(initial={'day':day})
    else:
        form = DaysForm()
        which_date = monday.date()
    employees = Employee.objects.all()
    
    # today
    employee_shift_maps_today = EmployeeShift.objects.filter(start_date=now.date())
    
    # this week
    week_start = now - datetime.timedelta(days=now.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    employee_shift_maps_this_week = EmployeeShift.objects.filter(start_date__gte=week_start, start_date__lte=week_end)
    
    # this month
    employee_shift_maps_this_month = EmployeeShift.objects.filter(start_date__month=now.month)

    now = timezone.now()

    # total TeamLeader,Manager,Department
    total_teamleader = TeamLeader.objects.count()
    total_manager = Manager.objects.count()
    total_employee = Employee.objects.count()
    total_departments = Department.objects.all().count()

    # this day
    total_leave_today = Leave.objects.filter(leave__status=LeaveStatus.APPROVED, start_date_at__lte=now.date(),
                                             end_date_at__gte=now.date()).count()
    total_unauthorized_leave_today = Leave.objects.filter(start_date_at__lte=now.date(), end_date_at__gte=now.date(),
                                                          status=Leave.UNAUTHORIZED).count()
    total_pending_leave_today = Leave.objects.filter(start_date_at__lte=now.date(), end_date_at__gte=now.date(),
                                                     leave__status=LeaveStatus.APPLIED).count()

    # this week
    week_start = now - datetime.timedelta(days=now.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    total_leave_week = Leave.objects.filter(leave__status=LeaveStatus.APPROVED, start_date_at__gte=week_start,
                                            end_date_at__lte=week_end).count()
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

    context = {
        'form':form,
        'employees':employees,
        'which_date':which_date,
        'today_all_worked_hours': all_emp_worked_hrs(employee_shift_maps_today),
        'this_week_all_worked_hours': all_emp_worked_hrs(employee_shift_maps_this_week),
        'this_month_all_worked_hours': all_emp_worked_hrs(employee_shift_maps_this_month),
        'total_leave_today': total_leave_today,
        'total_leave_week': total_leave_week,
        'total_leave_month': total_leave_month,
        'total_unauthorized_leave_today': total_unauthorized_leave_today,
        'total_unauthorized_leave_week': total_unauthorized_leave_week,
        'total_unauthorized_leave_month': total_unauthorized_leave_month,
        'total_pending_leave_today': total_pending_leave_today,
        'total_pending_leave_week': total_pending_leave_week,
        'total_pending_leave_month': total_pending_leave_month,
        'total_shift': total_shift,
        'total_manager': total_manager,
        'total_teamleader': total_teamleader,
        'total_departments': total_departments,
        'total_employee': total_employee,
    }
    return render(request, 'reports/report.html' ,context)
    
    
def all_emp_worked_hrs(employee_shift_maps_todays):
    # show in card
    today_all_worked_hours = datetime.timedelta(0)
    for employee_shift_map_today in employee_shift_maps_todays:
        if hasattr(employee_shift_map_today.employee_attendance, 'time_worked'):
            today_all_worked_hours += employee_shift_map_today.employee_attendance.time_worked()
    
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
    return today_all_worked_hours


@login_required
def shift_work_hours(request):
    """ All employees OT and Extra time worked"""
    if request.GET.get('daterange'):
        daterange = request.GET.get('daterange')
        daterange = daterange.split('-')
        start_date = daterange[0].strip()
        start_date = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
        end_date = daterange[1].strip()
        end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()
    else:
        now = timezone.now()
        start_date = now.date()
        end_date = now.date()
        
    employee_shift_maps_qs = EmployeeShift.objects.filter(start_date__gte=start_date, start_date__lte=end_date).order_by('start_date')
    pagination_context = get_fun_pagiantion(request, employee_shift_maps_qs, 'employee_shift_maps')
    pagination_context['start_date'] = start_date
    pagination_context['end_date'] = end_date
    
    return render(request, 'reports/shift_work_hours.html' ,pagination_context)


@login_required
def employees_leave_report(request):
    """ All employees leaves available and taken report by date range"""
    if request.GET.get('daterange'):
        daterange = request.GET.get('daterange')
        daterange = daterange.split('-')
        start_date = daterange[0].strip()
        start_date = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
        end_date = daterange[1].strip()
        end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()
    else:
        now = timezone.now()
        start_date = now.date()
        end_date = now.date()
    employees = Employee.objects.all()
    pagination_context = get_fun_pagiantion(request, employees, 'employees')
    pagination_context['start_date'] = start_date
    pagination_context['end_date'] = end_date
    return render(request, 'reports/emp_leaves_list.html' ,pagination_context)
    
    

@login_required
def employees_leave_report_detail(request, emp_id):
    """employee leaves available and taken report by date range"""
    if request.GET.get('year'):
        fy_year = request.GET.get('year')
        current_fy =FinancialYear.objects.get(id=fy_year)
    else:
        now = timezone.now()
        next_year = now.year + 1
        current_fy =FinancialYear.objects.filter(start_date__year__gte=now.year, end_date__year__lte=next_year).first()
    employee = get_object_or_404(Employee, id=emp_id)
    form = FinancialYearForm(initial={'year':current_fy.id})
    context = {
        'employee':employee,
        'start_date': FinancialYear.objects.get(id=form.initial['year']).start_date,
        'end_date': FinancialYear.objects.get(id=form.initial['year']).end_date,
        'leave_types': LeaveType.objects.all(),
        'current_fy': current_fy,
        'form':form
    }
    return render(request, 'reports/emp_leaves_detail.html', context)



@login_required
def update_leave_carry_cout(request, emp_id, leave_type_id, fyl_config_id):
    fy_leave_config = get_object_or_404(FinancialYearLeaveConfig, pk=fyl_config_id)
    emp = get_object_or_404(Employee, pk=leave_type_id)
    leave_type = get_object_or_404(LeaveType, pk=leave_type_id)
    emp_fyl, _ = EmployeeFYL.objects.get_or_create(fy_leave_config=fy_leave_config, employee=emp, leave_type=leave_type)
    
    leave_carry_form = LeaveCarryForm(request.POST or None, instance=emp_fyl)
    if request.method == 'POST':
        if leave_carry_form.is_valid():
            leave_carry = leave_carry_form.save(commit=False)
            leave_carry.leave_type = leave_type
            leave_carry.save()
            messages.success(request, '{} carry {} leave added to {}'.format(
                leave_carry_form.cleaned_data['carried_leave_no'],
                leave_carry_form.cleaned_data['leave_type'],
                leave_carry_form.cleaned_data['comment'],
                ))
            return HttpResponseRedirect(reverse('reports:employees_leave_report_detail', kwargs={'emp_id': emp.id}))
    
    return render(request, 'reports/emp_carry_leave_update.html', {'form': leave_carry_form})