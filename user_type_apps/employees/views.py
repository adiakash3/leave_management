from accounts.models import *
from departments.models import EmployeeDepartment
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, reverse
from helpers.web_paginators import *
from shifts.models import EmployeeShift
from .forms import *
from .models import *
import datetime
import logging
logger = logging.getLogger(__name__)

User = get_user_model()


@login_required
def employee_list(request):
    """
    Employee list with search
    """
    employees_qs = Employee.objects.all().order_by('-created_at')
    if request.GET.get('search'):
        query = request.GET.get('search')
        search_field = request.GET.get('search_field')
        if search_field.lower() == "":
            employees_qs = employees_qs
        if search_field.lower() == "email":
            employees_qs = employees_qs.filter(user__email__icontains=query)
            
        elif search_field.lower() == "mobile_number":
            employees_qs = employees_qs.filter(user__mobile_number__icontains=query)
            
        else:            
            employees_qs = employees_qs.filter(
                Q(user__email__icontains=query)
                | Q(user__mobile_number__icontains=query)
                )
    else:
        query = None
        search_field = None
    pagination_context = get_fun_pagiantion(request, employees_qs, 'employees')
    pagination_context['query'] = query
    pagination_context['search_field'] = search_field
    
    return render(request, 'employees/list.html', pagination_context)



@login_required
def employee_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/details.html', {'employee': employee})
    

@login_required
def employee_add(request):
    """
    Employee add
    """
    user_form = NewEmployeeCreationForm(request.POST or None)
    profile_form = NewEmployeeProfileCreationForm(request.POST or None)
    report_to_form = ReportToForm(request.POST or None)
    if request.method == "POST":
        
        if profile_form.is_valid() and user_form.is_valid() and report_to_form.is_valid():
            user = user_form.save()
            user.roles.add(Role.EMPLOYEE)
            # employee_group = Group.objects.get(name__iexact='employee')
            # user.groups.add(employee_group)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            employee, is_created = Employee.objects.get_or_create(user=user)
            employee.report_to = report_to_form.cleaned_data['report_to']
            employee.code = user_form.cleaned_data['code']
            employee.save()
            
            emp_department, is_created = EmployeeDepartment.objects.get_or_create(employee=employee)
            emp_department.department = report_to_form.cleaned_data['department']
            emp_department.joined_date = timezone.now()
            emp_department.save()
            
            logger.info("New employee created")
            messages.success(request, 'Employee created')
            return HttpResponseRedirect(reverse("employees:employee_list"))
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'report_to_form': report_to_form
    }
            
    return render(request=request,
                  template_name="employees/add.html",
                  context=context)

  
@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user_form = EmployeeUpdateForm(request.POST or None, instance=employee.user,initial={'code':employee.code})
    profile_form = NewEmployeeProfileCreationForm(request.POST or None, instance=employee.user.profile)
    if hasattr(employee , 'emp_department'):
        report_to_form = ReportToForm(request.POST or None, initial = {'report_to': employee.report_to,'department':employee.emp_department.department })
    else:
        report_to_form = ReportToForm(request.POST or None, initial = {'report_to': employee.report_to})

    if request.method == "POST":
        if profile_form.is_valid() and user_form.is_valid() and report_to_form.is_valid():
            user_form.save()
            profile_form.save()
            employee.report_to = report_to_form.cleaned_data['report_to']
            employee.code = user_form.cleaned_data['code']
            employee.save()
            
            emp_department, is_created = EmployeeDepartment.objects.get_or_create(employee=employee)
            emp_department.department = report_to_form.cleaned_data['department']
            emp_department.joined_date = timezone.now()
            emp_department.save()
            
            logger.info("Employee updated sucessfully")
            messages.success(request, 'Employee updated sucessfully')
            return HttpResponseRedirect(reverse("employees:employee_list"))
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'report_to_form': report_to_form
        
    }
    return render(request=request,
                  template_name="employees/edit.html",
                  context=context)
    
    
@login_required
def change_password(request, pk):
    """
    Employee password change by admin
    """
    user = get_object_or_404(User, pk=pk)
    form = EmployeePasswordChangeForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'Employee password was successfully updated!')
            return HttpResponseRedirect(reverse('employees:employee_edit', kwargs={'pk':user.employee.id}))
        else:
            messages.error(request, 'Please correct the error below.')
    return render(request, 'employees/change_password.html', {
        'form': form,
        'user':user
    })
    

@login_required
def employee_report(request, employee_id):
    if request.GET.get('datepicker'):
        daterange = request.GET.get('datepicker')
        current_date = daterange.strip()
        current_date = datetime.datetime.strptime(current_date, "%B, %Y").date()
    else:
        now = timezone.now()
        current_date = now.date()
        
    employee = get_object_or_404(Employee, id=employee_id)
    employee_shift_mappings = EmployeeShift.objects.filter(employee=employee,start_date__year=current_date.year, start_date__month=current_date.month).order_by('-start_date').exclude(employee_attendance=None)

    context = {
        'employee': employee,
        'employee_shift_mappings': employee_shift_mappings,
        'current_date': current_date
    }
    return render(request, 'employees/report.html', context)


@login_required
def employee_report_list(request):
    """
    Employee list with search and individual employee report
    """
    employees_qs = Employee.objects.all().order_by('-created_at')
    if request.GET.get('search'):
        query = request.GET.get('search')
        employees_qs = employees_qs.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(code__icontains=query)
            )
    else:
        query = None
    pagination_context = get_fun_pagiantion(request, employees_qs, 'employees')
    pagination_context['query'] = query
    return render(request, 'employees/employee_report_list.html', pagination_context)