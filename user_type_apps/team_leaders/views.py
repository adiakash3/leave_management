from accounts.models import *
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from departments.models import EmployeeDepartment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, reverse
from helpers.web_paginators import *
from push_notifications.web_notification import WebNotification
from .forms import *
from .models import *

import logging
logger = logging.getLogger(__name__)

User = get_user_model()


@login_required
def team_leader_list(request):
    """
    TeamLeader list with search
    """
    team_leaders_qs = TeamLeader.objects.all().order_by('-created_at')
    if request.GET.get('search'):
        query = request.GET.get('search')
        search_field = request.GET.get('search_field')
        if search_field.lower() == "":
            team_leaders_qs = team_leaders_qs
        if search_field.lower() == "email":
            team_leaders_qs = team_leaders_qs.filter(employee__user__email__icontains=query)

        elif search_field.lower() == "mobile_number":
            team_leaders_qs = team_leaders_qs.filter(employee__user__mobile_number__icontains=query)

        else:
            team_leaders_qs = team_leaders_qs.filter(
                Q(employee__user__email__icontains=query)
                | Q(employee__user__mobile_number__icontains=query)
                )
    else:
        query = None
        search_field = None
    pagination_context = get_fun_pagiantion(request, team_leaders_qs, 'team_leaders')
    pagination_context['query'] = query
    pagination_context['search_field'] = search_field

    return render(request, 'team_leaders/list.html', pagination_context)



@login_required
def team_leader_view(request, pk):
    team_leader = get_object_or_404(TeamLeader, pk=pk)
    return render(request, 'team_leaders/details.html', {'team_leader': team_leader})


@login_required
def team_leader_add(request):
    """
    TeamLeader add
    """
    user_form = NewTeamLeaderCreationForm(request.POST or None)
    profile_form = NewTeamLeaderProfileCreationForm(request.POST or None)
    report_to_form = ReportToForm(request.POST or None)

    if request.method == "POST":

        if profile_form.is_valid() and user_form.is_valid() and report_to_form.is_valid():
            user = user_form.save()
            user.roles.add(Role.TEAM_LEADER)
            # team_leader_group = Group.objects.get(name__iexact='team_leader')
            # user.groups.add(team_leader_group)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            employee, _ = Employee.objects.get_or_create(user=user)
            employee.code = user_form.cleaned_data['code']
            employee.report_to = report_to_form.cleaned_data['report_to']
            employee.save()
            team_leader, is_created = TeamLeader.objects.get_or_create(employee=employee)
            tl_department,is_created = EmployeeDepartment.objects.get_or_create(employee=employee)
            tl_department.department = report_to_form.cleaned_data['department']
            tl_department.joined_date = timezone.now()
            tl_department.save()
            logger.info("New team_leader created")
            messages.success(request, 'Team Leader created')
            return HttpResponseRedirect(reverse("team_leaders:team_leader_list"))

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'report_to_form': report_to_form
    }

    return render(request=request,
                  template_name="team_leaders/add.html",
                  context=context)


@login_required
def team_leader_edit(request, pk):
    team_leader = get_object_or_404(TeamLeader, pk=pk)
    user_form = TeamLeaderUpdateForm(request.POST or None, instance=team_leader.employee.user,initial={'code':team_leader.employee.code})
    profile_form = NewTeamLeaderProfileCreationForm(request.POST or None, instance=team_leader.employee.user.profile)
    if hasattr(team_leader.employee , 'emp_department'):
        report_to_form = ReportToForm(request.POST or None, initial = {'report_to': team_leader.employee.report_to,'code':team_leader.employee.code,'department':team_leader.employee.emp_department.department })
    else:
        report_to_form = ReportToForm(request.POST or None, initial={'report_to': team_leader.employee.report_to,'code':team_leader.employee.code})
    if request.method == "POST":
        if profile_form.is_valid() and user_form.is_valid() and report_to_form.is_valid():
            user_form.save()
            profile_form.save()
            team_leader.employee.report_to = report_to_form.cleaned_data['report_to']
            team_leader.employee.code = user_form.cleaned_data['code']
            team_leader.employee.save()
            tl_department, is_created = EmployeeDepartment.objects.get_or_create(employee=team_leader.employee)
            tl_department.department = report_to_form.cleaned_data['department']
            tl_department.joined_date = timezone.now()
            tl_department.save()
            logger.info("Team Leader updated sucessfully")
            messages.success(request, 'Team Leader updated sucessfully')
            return HttpResponseRedirect(reverse("team_leaders:team_leader_list"))
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'report_to_form': report_to_form

    }
    return render(request=request,
                  template_name="team_leaders/edit.html",
                  context=context)


@login_required
def change_password(request, pk):
    """
    TeamLeader password change by admin
    """
    user = get_object_or_404(User, pk=pk)
    form = TeamLeaderPasswordChangeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'Team Leader password was successfully updated!')
            WebNotification().send_only_notification_to_user([user,], title="your profile is updated", message="your profile is updated")
            return HttpResponseRedirect(reverse('team_leaders:team_leader_edit', kwargs={'pk':user.employee.team_leader.id}))
        else:
            messages.error(request, 'Please correct the error below.')
    return render(request, 'team_leaders/change_password.html', {
        'form': form,
        'user':user
    })

@login_required
def my_employee_list(request,pk):
    team_leader_user_id= TeamLeader.objects.filter(id=pk)
    userID=0
    for id in team_leader_user_id:
        userID=id.employee.user.id
    employee_qs = Employee.objects.filter(report_to =userID)

    query = request.GET.get('search')
    if query:
        employee_qs = employee_qs.filter(Q(name__icontains=query))
    else:
        query = None
    pagination_context = get_fun_pagiantion(request, employee_qs, 'employees')
    pagination_context['query'] = query
    return render(request,'team_leaders/my_team_list.html',pagination_context)