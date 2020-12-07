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
from user_type_apps.team_leaders.models import *
from .forms import *
from .models import *


import logging
logger = logging.getLogger(__name__)

User = get_user_model()


@login_required
def manager_list(request):
    """
    Manager list with search
    """
    managers_qs = Manager.objects.all().order_by('-created_at')
    if request.GET.get('search'):
        query = request.GET.get('search')
        search_field = request.GET.get('search_field')
        if search_field.lower() == "":
            managers_qs = managers_qs
        if search_field.lower() == "email":
            managers_qs = managers_qs.filter(employee__user__email__icontains=query)
            
        elif search_field.lower() == "mobile_number":
            managers_qs = managers_qs.filter(employee__user__mobile_number__icontains=query)
            
        else:            
            managers_qs = managers_qs.filter(
                Q(employee__user__email__icontains=query)
                | Q(employee__user__mobile_number__icontains=query)
                )
    else:
        query = None
        search_field = None
    pagination_context = get_fun_pagiantion(request, managers_qs, 'managers')
    pagination_context['query'] = query
    pagination_context['search_field'] = search_field
    
    return render(request, 'managers/list.html', pagination_context)



@login_required
def manager_view(request, pk):
    manager = get_object_or_404(Manager, pk=pk)
    return render(request, 'managers/details.html', {'manager': manager})
    

@login_required
def manager_add(request):
    """
    Manager add
    """
    user_form = NewManagerCreationForm(request.POST or None)
    profile_form = NewManagerProfileCreationForm(request.POST or None)
    report_to_form = ReportToForm(request.POST or None)
    if request.method == "POST":
        
        if profile_form.is_valid() and user_form.is_valid() and report_to_form.is_valid():
            user = user_form.save()
            user.roles.add(Role.MANAGER)
            # manager_group = Group.objects.get(name__iexact='manager')
            # user.groups.add(manager_group)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            employee, _ = Employee.objects.get_or_create(user=user)
            employee.report_to = report_to_form.cleaned_data['report_to']
            employee.code = user_form.cleaned_data['code']
            employee.save()
            manager, is_created = Manager.objects.get_or_create(employee=employee)
            manager_department, is_created = EmployeeDepartment.objects.get_or_create(employee=employee)
            manager_department.department = report_to_form.cleaned_data['department']
            manager_department.joined_date = timezone.now()
            manager_department.save()
            logger.info("New manager created")
            messages.success(request, 'Manager created')
            return HttpResponseRedirect(reverse("managers:manager_list"))
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'report_to_form': report_to_form
    }
            
    return render(request=request,
                  template_name="managers/add.html",
                  context=context)

  
@login_required
def manager_edit(request, pk):
    manager = get_object_or_404(Manager, pk=pk)
    user_form = ManagerUpdateForm(request.POST or None, instance=manager.employee.user,initial={'code':manager.employee.code})
    profile_form = NewManagerProfileCreationForm(request.POST or None, instance=manager.employee.user.profile)
    if hasattr(manager.employee , 'emp_department'):
        report_to_form = ReportToForm(request.POST or None, initial = {'report_to': manager.employee.report_to,'code':manager.employee.code,'department':manager.employee.emp_department.department })
    else:
        report_to_form = ReportToForm(request.POST or None, initial={'report_to': manager.employee.report_to,'code':manager.employee.code})
    if request.method == "POST":
        if profile_form.is_valid() and user_form.is_valid() and report_to_form.is_valid():
            user_form.save()
            profile_form.save()
            manager.employee.report_to = report_to_form.cleaned_data['report_to']
            manager.employee.code = user_form.cleaned_data['code']
            manager.employee.save()
            manager_department, is_created = EmployeeDepartment.objects.get_or_create(employee=manager.employee)
            manager_department.department = report_to_form.cleaned_data['department']
            manager_department.joined_date = timezone.now()
            manager_department.save()
            logger.info("Manager updated sucessfully")
            messages.success(request, 'Manager updated sucessfully')
            return HttpResponseRedirect(reverse("managers:manager_list"))
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'report_to_form': report_to_form,        
    }
    return render(request=request,
                  template_name="managers/edit.html",
                  context=context)
    
    
@login_required
def change_password(request, pk):
    """
    Manager password change by admin
    """
    user = get_object_or_404(User, pk=pk)
    form = ManagerPasswordChangeForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'Manager password was successfully updated!')
            return HttpResponseRedirect(reverse('managers:manager_edit', kwargs={'pk':user.employee.manager.id}))
        else:
            messages.error(request, 'Please correct the error below.')
    return render(request, 'managers/change_password.html', {
        'form': form,
        'user':user
    })

@login_required
def my_employee_list(request,pk):
    manager_user_id= Manager.objects.filter(id=pk)
    userID=0
    for id in manager_user_id:
        userID=id.employee.user.id
    manager_user_id = Employee.objects.filter(report_to =userID)

    print(manager_user_id)

    query = request.GET.get('search')
    if query:
        manager_user_id = manager_user_id.filter(Q(name__icontains=query))
    else:
        query = None
    pagination_context = get_fun_pagiantion(request, manager_user_id, 'employees')
    pagination_context['query'] = query
    return render(request,'managers/my_team_list.html',pagination_context)

def my_team_list(request,pk):
    manager_user_id= Manager.objects.filter(id=pk)
    userID=0
    for id in manager_user_id:
        userID=id.employee.user.id
    manager_user_id = TeamLeader.objects.filter(employee__report_to =userID)

    print(manager_user_id)

    query = request.GET.get('search')
    if query:
        manager_user_id = manager_user_id.filter(Q(name__icontains=query))
    else:
        query = None
    pagination_context = get_fun_pagiantion(request, manager_user_id, 'employees')
    pagination_context['query'] = query
    return render(request,'managers/my_teamlead_list.html',pagination_context)