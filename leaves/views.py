from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, reverse, HttpResponseRedirect
from .forms import *
from .models import *
from helpers.web_paginators import get_fun_pagiantion
from accounts.models import Role
from datetime import timedelta



@login_required
def leaves_all_list(request):
    bool_var = False
    if  request.user.roles.filter(id__in=[Role.ADMIN]).exists():
        leaves_qs = Leave.objects.filter(status__iexact=Leave.APPLIED).order_by('-applied_on')
        bool_var = True
    elif request.user.roles.filter(id__in=[Role.TEAM_LEADER]).exists():
        leaves_qs = Leave.objects.filter(status=Leave.APPLIED,applied_by__roles__id=Role.TEAM_LEADER).order_by('-applied_on')
    elif request.user.roles.filter(id__in=[Role.MANAGER]).exists():
        leaves_qs = Leave.objects.filter(status=Leave.APPLIED,applied_by__roles__id=Role.MANAGER).order_by('-applied_on')

    if request.GET.get('search') or request.GET.get('search_field'):
        query = request.GET.get('search')
        search_field = request.GET.get('search_field')
        if search_field.lower() == "":
            leaves_qs = leaves_qs
        if search_field.lower() == "applied_by":
            leaves_qs = leaves_qs.filter(Q(applied_by__email__icontains=query)|
                                         Q(applied_by__first_name__icontains=query)|
                                         Q(applied_by__last_name__icontains=query))
            
        elif search_field.lower() == "leave_status":
            leaves_qs = leaves_qs.filter(Q(status__icontains=query)|Q(leave__status__icontains=query))

        elif search_field.lower() == "manager":
            leaves_qs = leaves_qs.filter(applied_by__roles__id=Role.MANAGER)

        elif search_field.lower() == "team_leader":
            leaves_qs = leaves_qs.filter(applied_by__roles__id=Role.TEAM_LEADER)

        else:
            leaves_qs = leaves_qs.filter(
                Q(applied_by__email__icontains=query)|
                Q(applied_by__first_name__icontains=query)|
                Q(applied_by__last_name__icontains=query) |
                Q(status__icontains=query)|
                Q(leave__status__icontains=query)
                )
    else:
        query = None
        search_field = None
    pagination_context = get_fun_pagiantion(request, leaves_qs, 'leaves')
    pagination_context['query'] = query
    pagination_context['bool_var'] = bool_var
    pagination_context['search_field'] = search_field
    
    return render(request, 'leaves/list.html', pagination_context)


@login_required
def leave_view(request, leave_id):
    leave_obj = get_object_or_404(Leave, pk=leave_id)
    return render(request, 'leaves/view.html', {'leave':leave_obj})
    
    
@login_required
def leave_approve(request, leave_id):
    leave_obj = get_object_or_404(Leave, pk=leave_id)
    leave_status_obj, _ = LeaveStatus.objects.get_or_create(leave=leave_obj)
    if request.method == 'POST':
        if request.POST.get('choice') == 'approve':
            leave_status_obj.status = LeaveStatus.APPROVED
            leave_status_obj.comments = request.POST.get('comments')
            leave_status_obj.approver = request.user
            leave_status_obj.approver_action_at = timezone.now()
            leave_status_obj.save()
            messages.success(request,
                             '{} {} leave has been approved'.format(leave_obj.applied_by, leave_obj.leave_type.name))
            return HttpResponseRedirect(reverse('leaves:leave_view', kwargs={'leave_id': leave_id}))
        if request.POST.get('choice') == 'reject':
            leave_status_obj.status = LeaveStatus.REJECTED
            leave_status_obj.comments = request.POST.get('comments')
            leave_status_obj.approver = request.user
            leave_status_obj.approver_action_at = timezone.now()
            leave_status_obj.save()
            messages.success(request,
                             '{} {} leave has been rejected'.format(leave_obj.applied_by, leave_obj.leave_type.name))
            return HttpResponseRedirect(reverse('leaves:leave_view', kwargs={'leave_id': leave_id}))


@login_required
def leave_type_list(request):
    leave_type_qs = LeaveType.objects.all()
    query = request.GET.get('search')
    if query:
        leave_type_qs = leave_type_qs.filter(Q(name__icontains=query))
    else:
        query = None
    pagination_context = get_fun_pagiantion(request, leave_type_qs, 'leavetypes')
    pagination_context['query'] = query
    return render(request,'leaves/leave_type/list.html',pagination_context)


@login_required
def leave_type_add(request):
    leave_type_form = LeaveTypeCreationForm(request.POST or None)
    if request.method == 'POST' and leave_type_form.is_valid():
        leave_type_form.save()
        messages.success(request,'Leave Type added successfully')
        return HttpResponseRedirect(reverse('leaves:leave_type_list'))
    context = {'leave_type_form':leave_type_form}
    return render(request,'leaves/leave_type/add.html',context)


@login_required
def leave_type_edit(request,leave_type_id):
    leave_obj = get_object_or_404(LeaveType, pk=leave_type_id)
    leave_type_form = LeaveTypeCreationForm(request.POST or None, instance=leave_obj)
    if request.method == 'POST' and leave_type_form.is_valid():
        leave_type_form.save()
        messages.success(request, 'Leave Type updated successfully')
        return HttpResponseRedirect(reverse('leaves:leave_type_list'))
    context = {'leave_type_form': leave_type_form}
    return render(request, 'leaves/leave_type/edit.html', context)


@login_required
def leave_type_view(request,leave_type_id):
    leave_obj = get_object_or_404(LeaveType, pk=leave_type_id)
    context = {'leave_obj':leave_obj}
    return render(request,'leaves/leave_type/detail.html',context)


@login_required
def financial_year_leaves(request):
    financial_year_leave_qs = FinancialYearLeaveConfig.objects.all()
    pagination_context = get_fun_pagiantion(request, financial_year_leave_qs, 'financial_leave_years')
    return render(request,'leaves/financial_leave/list.html',pagination_context)


@login_required
def financial_year_leave_add(request):
    fyl_form = FylCreationForm(request.POST or None)
    if request.method == 'POST' and fyl_form.is_valid():
        fyl_form.save()
        messages.success(request,'Financial year leave added successfully')
        return HttpResponseRedirect(reverse('leaves:financial_year_leaves'))
    context = {'fyl_form':fyl_form}
    return render(request,'leaves/financial_leave/add.html',context)


@login_required
def financial_year_leave_edit(request,fyl_id):
    fyl_obj = get_object_or_404(FinancialYearLeaveConfig,pk=fyl_id)
    fyl_form = FylEditForm(request.POST or None,instance=fyl_obj)
    if request.method == 'POST' and fyl_form.is_valid():
        fyl_form.save()
        messages.success(request,'Financial year leave updated successfully')
        return HttpResponseRedirect(reverse('leaves:financial_year_leaves'))
    context = {'fyl_form':fyl_form}
    return render(request,'leaves/financial_leave/edit.html',context)


@login_required
def financial_year_leave_view(request,fyl_id):
    fyl_obj = get_object_or_404(FinancialYearLeaveConfig,pk=fyl_id)
    context = {'fyl_obj':fyl_obj}
    return render(request,'leaves/financial_leave/view.html',context)


@login_required
def financial_year_list(request):
    financial_year_qs = FinancialYear.objects.all().order_by('-id')
    pagination_context = get_fun_pagiantion(request, financial_year_qs, 'financialyear')
    return render(request,'leaves/financial_year/list.html',pagination_context)

@login_required
def financial_year_add(request):
    financial_year_form = FinancialYearCreationForm(request.POST or None)
    if request.method == 'POST' and financial_year_form.is_valid():
        financial_year_form.save()
        messages.success(request,'Financial year added successfully')
        return HttpResponseRedirect(reverse('leaves:financial_year_list'))
    context = {'financial_year_form':financial_year_form}
    return render(request,'leaves/financial_year/add.html',context)


@login_required
def leave_add(request):
    leave_form = LeaveCreationForm(request.POST or None)
    if request.method == 'POST' and leave_form.is_valid():
        start_date_at = leave_form.cleaned_data.get('start_date_at')
        end_date_at = leave_form.cleaned_data.get('end_date_at')
        #######get already applied leaves dates#######
        already_applied_leaves_dates = []
        for each in Leave.objects.filter(applied_by=leave_form.cleaned_data.get('applied_by'),leave__status=LeaveStatus.APPROVED):
            dates = each.end_date_at - each.start_date_at
            for i in range(dates.days + 1):
                days = each.start_date_at + timedelta(days=i)
                already_applied_leaves_dates.append(days)
        #########currently applying leaves###########
        diff = end_date_at - start_date_at
        current_leave_dates = [start_date_at + timedelta(days=i) for i in range(diff.days + 1)]
        for each in current_leave_dates:
            if each in list(set(already_applied_leaves_dates)):
                applied_dates_wrt_applying_now = [str(value)[:10] for value in current_leave_dates if value in list(set(already_applied_leaves_dates))]
                messages.error(request, "Leaves are already approved on the corresponding  dates: {}".format(applied_dates_wrt_applying_now))
                return HttpResponseRedirect(reverse('leaves:leave_add'))
        leave = leave_form.save()
        leave.save()
        leavestatus, is_created = LeaveStatus.objects.get_or_create(leave=leave)
        leavestatus.status = LeaveStatus.APPLIED
        leavestatus.approver = leave.applied_by.report_to
        leavestatus.save()
        messages.success(request,'Leave added successfully')
        return HttpResponseRedirect(reverse('leaves:leaves_all_list'))
    context = {'leave_form':leave_form}
    return render(request,'leaves/add.html',context)

@login_required
def pending_leave_today(request):
    now = timezone.now()
    total_pending_leave_today = Leave.objects.filter(start_date_at__lte=now.date(), end_date_at__gte=now.date(),
                                                     leave__status=LeaveStatus.APPLIED)
    pagination_context = get_fun_pagiantion(request, total_pending_leave_today, 'total_pending_leave_today')
    return render(request,'leaves/pending_leave/today.html',pagination_context)


@login_required
def pending_leave_week(request):
    now = timezone.now()
    week_start = now - datetime.timedelta(days=now.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    print(week_start)
    total_pending_leave_week = Leave.objects.filter(start_date_at__gte=week_start, end_date_at__lte=week_end,
                                                    leave__status=LeaveStatus.APPLIED)
    pagination_context = get_fun_pagiantion(request, total_pending_leave_week, 'total_pending_leave_week')
    return render(request,'leaves/pending_leave/week.html',pagination_context)



@login_required
def pending_leave_month(request):
    now = timezone.now()

    total_pending_leave_month = Leave.objects.filter(start_date_at__month=now.month,
                                                     leave__status=LeaveStatus.APPLIED)
    print(total_pending_leave_month)
    pagination_context = get_fun_pagiantion(request, total_pending_leave_month, 'total_pending_leave_month')
    return render(request,'leaves/pending_leave/month.html',pagination_context)

@login_required
def unauthorized_leave_today(request):
    now = timezone.now()
    total_unauthorized_leave_today = Leave.objects.filter(start_date_at__lte=now.date(), end_date_at__gte=now.date(),
                                                          status=Leave.UNAUTHORIZED)
    pagination_context = get_fun_pagiantion(request, total_unauthorized_leave_today, 'total_unauthorized_leave_today')
    return render(request,'leaves/unauthorized_leave/today.html',pagination_context)

@login_required
def unauthorized_leave_week(request):
    now = timezone.now()
    week_start = now - datetime.timedelta(days=now.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    total_unauthorized_leave_week = Leave.objects.filter(start_date_at__gte=week_start, end_date_at__lte=week_end,
                                                         status=Leave.UNAUTHORIZED)
    pagination_context = get_fun_pagiantion(request, total_unauthorized_leave_week, 'total_unauthorized_leave_week')
    return render(request,'leaves/unauthorized_leave/week.html',pagination_context)

@login_required
def unauthorized_leave_month(request):
    now = timezone.now()
    total_unauthorized_leave_month = Leave.objects.filter(start_date_at__month=now.month,
                                                          status=Leave.UNAUTHORIZED)
    pagination_context = get_fun_pagiantion(request, total_unauthorized_leave_month, 'total_unauthorized_leave_month')
    return render(request,'leaves/unauthorized_leave/month.html',pagination_context)

@login_required
def approved_leave_today(request):
    now = timezone.now()
    total_leave_today = Leave.objects.filter(leave__status=LeaveStatus.APPROVED,start_date_at__lte=now.date(), end_date_at__gte=now.date())
    pagination_context = get_fun_pagiantion(request, total_leave_today, 'total_leave_today')
    return render(request,'leaves/approved_leave/today.html',pagination_context)

@login_required
def approved_leave_week(request):
    now = timezone.now()
    week_start = now - datetime.timedelta(days=now.weekday())
    week_end = week_start + datetime.timedelta(days=6)
    total_leave_week = Leave.objects.filter(leave__status=LeaveStatus.APPROVED, start_date_at__gte=week_start,
                                            end_date_at__lte=week_end)
    pagination_context = get_fun_pagiantion(request, total_leave_week, 'total_leave_week')
    return render(request,'leaves/approved_leave/today.html',pagination_context)

@login_required
def approved_leave_month(request):
    now = timezone.now()
    total_leave_month = Leave.objects.filter(start_date_at__month=now.month)
    pagination_context = get_fun_pagiantion(request, total_leave_month, 'total_leave_month')
    return render(request,'leaves/approved_leave/month.html',pagination_context)