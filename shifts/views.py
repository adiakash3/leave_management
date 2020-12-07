from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse
from helpers.web_paginators import *
from io import StringIO
from .forms import *
from .models import *
import csv
import itertools

import logging
logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
def shift_list(request):
    """
    Holiday list with search
    """
    shift_qs = Shift.objects.all().order_by('-created_at')
    query = request.GET.get('search')
    if request.GET.get('search'):
        query = request.GET.get('search')
        search_field = request.GET.get('search_field')
        if search_field.lower() == "":
            shift_qs = shift_qs
        if search_field.lower() == "name":
            shift_qs = shift_qs.filter(name__icontains=query)
            
        else:            
            shift_qs = shift_qs.filter(
                Q(name__icontains=query)
            )
            
    else:
        query = None
        search_field = None
    pagination_context = get_fun_pagiantion(request, shift_qs, 'shifts')
    pagination_context['query'] = query
    pagination_context['search_field'] = search_field
    return render(request,'shifts/list.html',pagination_context)


@login_required
def shift_add(request):
    shift_form = ShiftForm(request.POST or None)
    if request.method == 'POST':
        if shift_form.is_valid():
            shift_form.save()
            logger.info("New shift created")
            messages.success(request, 'Shift created successfully')
            return HttpResponseRedirect(reverse("shifts:shift_list"))
    context = {
        'form':shift_form
    }
    return render(request=request,
                  template_name="shifts/add.html",
                  context=context)


@login_required
def shift_edit(request,shift_id):
    shift = get_object_or_404(Shift, pk=shift_id)
    shift_form = ShiftForm(request.POST or None, instance=shift)
    if request.method == 'POST':
        if shift_form.is_valid():
            shift_form.save()
            logger.info("shift updated")
            messages.success(request, 'Shift updated successfully')
            return HttpResponseRedirect(reverse("shifts:shift_list"))
    context = {
        'form': shift_form
    }
    return render(request=request,
                  template_name="shifts/edit.html",
                  context=context)


@login_required
def shift_view(request, shift_id):
    shift = get_object_or_404(Shift, pk=shift_id)
    return render(request, "shifts/view.html", {'shift':shift})


def lower_first(iterator):
    return itertools.chain([next(iterator).lower()], iterator)


@login_required
def shift_csv_import(request):
    """ import shift from csv
    1. name
    2. shift start time
    3. shift end time
    4. shift code
    """
    try:
        if not request.FILES.get('csv', False):
            return HttpResponseRedirect(reverse('shifts:shift_list'))
        shift_csv_file = request.FILES['csv']

        # if not csv file
        if not shift_csv_file.name.endswith(".csv"):
            return HttpResponseRedirect(reverse('shifts:shift_list'))

        file_data = StringIO(shift_csv_file.read().decode())
        decoded_csv_file = csv.DictReader(lower_first(file_data))
        imported_shifts = []
        no_of_imported_count = 0

        for row in decoded_csv_file:
            logger.info(row)
            shift_dict = dict(row)
            name = shift_dict['shift name'].strip()
            code = shift_dict['shift code'].strip()
            start_time = shift_dict['start time'].strip()
            end_time = shift_dict['end time'].strip()
                
            if not Shift.objects.filter(code__iexact=code).exists():
                shift_obj = Shift(
                    name = name,
                    code = code,
                    start_time = start_time,
                    end_time = end_time
                )
                imported_shifts.append(shift_obj)
                no_of_imported_count +=1
        Shift.objects.bulk_create(imported_shifts)
        messages.success(request, "Successfully imported {} Shifts from CSV file".format(no_of_imported_count))
    except Exception as e:
        logger.info("unable to import shift csv file {}".format(e))
        messages.warning(request, "unable to import Shift csv file {}".format(e))

    return HttpResponseRedirect(reverse('shifts:shift_list'))


@login_required
def import_employee_attendance(request):
    """Import employee attendance using employee code and shift code"""
    try:
        if not request.FILES.get('csv', False):
            messages.warning(request, "please choose CSV file")
            return HttpResponseRedirect(reverse('shifts:employee_shift_list'))
        shift_csv_file = request.FILES['csv']

        # if not csv file
        if not shift_csv_file.name.endswith(".csv"):
            messages.warning(request, 'Supported files only CSV types')
            return HttpResponseRedirect(reverse('shifts:employee_shift_list'))

        file_data = StringIO(shift_csv_file.read().decode())
        decoded_csv_file = csv.DictReader(lower_first(file_data))
        no_of_attendance_imported = 0   
        for row in decoded_csv_file:
            try:
                logger.info(row)
                shift_dict = dict(row)
                             
                attendace_date = shift_dict.get('attendance date')
                if not attendace_date:
                    continue 
                attendace_date = datetime.datetime.strptime(attendace_date, '%d-%b-%Y').date()
                employee_code = shift_dict.get('employee code')
                shift_code = shift_dict.get('shift code')
                in_time = shift_dict.get('in time')
                if len(in_time) > 5:
                    parse_format = '%H:%M:%S'
                else:
                    parse_format = '%H:%M'
                in_time = datetime.datetime.strptime(in_time,parse_format).time()
                
                out_time = shift_dict.get('out time')
                if len(out_time) > 5:
                    parse_format = '%H:%M:%S'
                else:
                    parse_format = '%H:%M'
                out_time = datetime.datetime.strptime(out_time, parse_format).time()
                
                if Employee.objects.filter(code__iexact=employee_code).exists():
                    emp = get_object_or_404(Employee, code=employee_code)
                    shift = get_object_or_404(Shift, code=shift_code)
                    # create shift mapping
                    employee_shift_map, is_created = EmployeeShift.objects.get_or_create(
                                                        employee=emp,
                                                        shift=shift,
                                                        start_date = attendace_date,
                                                        end_date = attendace_date
                                                    )
                    # create attendance
                    employee_attendance, _ = EmployeeAttendance.objects.get_or_create(
                                                            employee=emp, 
                                                            check_in=in_time,
                                                            check_out=out_time,
                                                            date=attendace_date
                                            )
                    employee_shift_map.employee_attendance = employee_attendance
                    employee_shift_map.save()
                    
                    # create late exempt
                    if in_time > shift.start_time:
                        late_exempt, is_created = LateExempt.objects.get_or_create(employee_shift=employee_shift_map)
                        late_exempt.late_type = LateExempt.LATE_COMING
                        late_exempt.check_in=in_time
                        late_exempt.comment = "{} late to office".format(emp)
                        late_exempt.save()
                        if is_created:
                            late_exempt_status = LateExemptStatus()
                            late_exempt_status.late_exempt = late_exempt
                            late_exempt_status.status = LateExemptStatus.RECEIVED
                            late_exempt_status.report_to = emp.report_to.employee
                            late_exempt_status.save()
                            
                    if  out_time < shift.end_time:
                        late_exempt, is_created = LateExempt.objects.get_or_create(employee_shift=employee_shift_map)
                        late_exempt.late_type = LateExempt.EARLY_GOING
                        late_exempt.check_in=out_time
                        late_exempt.comment = "{} Early leaving from office".format(emp)
                        late_exempt.save()
                        if is_created:
                            late_exempt_status = LateExemptStatus()
                            late_exempt_status.late_exempt = late_exempt
                            late_exempt_status.status = LateExemptStatus.RECEIVED
                            late_exempt_status.report_to = emp.report_to.employee
                            late_exempt_status.save()
                        
                    no_of_attendance_imported +=1
                        
                    logger.info("attendance imported {}".format(employee_code))
            except Exception as e:
                logger.info("unable to import employee attendance reason {}".format(e))
            
        messages.success(request, "Successfully imported or updated {} employee attendace".format(no_of_attendance_imported))
    except Exception as e:
        logger.info("unable to import employee attendance csv file {}".format(e))
        messages.warning(request, "unable to import employee attendance csv file {}".format(e))

    return HttpResponseRedirect(reverse('shifts:employee_shift_list'))


@login_required
def break_list(request):
    """
    Break list with search
    """
    break_qs = Break.objects.all().order_by('-created_at')
    query = request.GET.get('search')
    if request.GET.get('search'):
        query = request.GET.get('search')
        search_field = request.GET.get('search_field')
        if search_field.lower() == "":
            break_qs = break_qs
        if search_field.lower() == "name":
            break_qs = break_qs.filter(name__icontains=query)
        else:
            break_qs = break_qs.filter(
                Q(name__icontains=query)
            )
    else:
        query = None
        search_field = None
    pagination_context = get_fun_pagiantion(request, break_qs, 'breaks')
    pagination_context['query'] = query
    pagination_context['search_field'] = search_field
    return render(request,'breaks/list.html',pagination_context)

@login_required
def break_add(request):
    break_form = BreakForm(request.POST or None)
    if request.method == 'POST':
        if break_form.is_valid():
            break_form.save()
            logger.info("New Break created")
            messages.success(request, 'Break created successfully')
            return HttpResponseRedirect(reverse("shifts:break_list"))
    context = {
        'form':break_form
    }
    return render(request=request,
                  template_name="breaks/add.html",
                  context=context)

@login_required
def break_edit(request,break_id):
    breaks = get_object_or_404(Break, pk=break_id)
    break_form = BreakForm(request.POST or None, instance=breaks)
    if request.method == 'POST':
        if break_form.is_valid():
            break_form.save()
            logger.info("break updated")
            messages.success(request, 'Break updated successfully')
            return HttpResponseRedirect(reverse("shifts:break_list"))
    context = {
        'form': break_form
    }
    return render(request=request,
                  template_name="breaks/edit.html",
                  context=context)

@login_required
def break_view(request, break_id):
    breaks = get_object_or_404(Break, pk=break_id)
    return render(request, "breaks/view.html", {'breaks':breaks})


@login_required
def employee_shift_add(request):
    """
        Employee shift add
    """
    employee_shift_form = EmployeeShiftForm(request.POST or None)
    if request.method == 'POST':
        if employee_shift_form.is_valid():
            employee_shift_form.save()
            logger.info("Employee shift created")
            messages.success(request, 'Employee shift successfully')
            return HttpResponseRedirect(reverse("shifts:employee_shift_list"))
    context = {
        'form':employee_shift_form
    }
    return render(request=request,
                  template_name="employee_shift/add.html",
                  context=context)


@login_required
def employee_shift_list(request):
    """
    Employee shift list
    """
    employee_shift_qs = EmployeeShift.objects.all().order_by('-start_date')
    if request.GET.get('search'):
        query = request.GET.get('search')
        employee_shift_qs = employee_shift_qs.filter(
            Q(shift__name__icontains=query) |
            Q(employee__code__icontains=query)|
            Q(employee__user__email__icontains=query)
        )
    else:
        query = None

    pagination_context = get_fun_pagiantion(request, employee_shift_qs, 'employee_shifts')
    pagination_context['query'] = query
    return render(request,'employee_shift/list.html',pagination_context)


@login_required
def import_assign_employee_shift(request):
    """Import employee future shifts which should be assigned"""
    try:
        if not request.FILES.get('csv', False):
            messages.warning(request, "please choose CSV file")
            return HttpResponseRedirect(reverse('shifts:employee_shift_list'))
        shift_csv_file = request.FILES['csv']

        # if not csv file
        if not shift_csv_file.name.endswith(".csv"):
            messages.warning(request, 'Supported files only CSV types')
            return HttpResponseRedirect(reverse('shifts:employee_shift_list'))

        file_data = StringIO(shift_csv_file.read().decode())
        decoded_csv_file = csv.DictReader(lower_first(file_data))
        no_of_employee_shift_imported = 0   
        for row in decoded_csv_file:
            try:
                logger.info(row)
                shift_dict = dict(row)
                             
                employee_code = shift_dict['employee code'].strip()
                shift_code = shift_dict['shift code'].strip()
                start_date = shift_dict['start date'].strip()
                end_date = shift_dict['end date'].strip()
                
                if not Employee.objects.filter(code__iexact=employee_code):
                    continue 
                if not Shift.objects.filter(code__iexact=shift_code):
                    continue 
                start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
                end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()
                
                emp = get_object_or_404(Employee, code__iexact=employee_code)
                shift = get_object_or_404(Shift, code__iexact=shift_code)
                # create shift mapping
                employee_shift_map, is_created = EmployeeShift.objects.get_or_create(
                                                    employee=emp,
                                                    shift=shift,
                                                    start_date = start_date,
                                                    end_date = end_date)
                                                
                    
                no_of_employee_shift_imported +=1
                    
                logger.info("Employee shift assign imported {}".format(employee_code))
            except Exception as e:
                logger.info("unable to import employee shift mapping reason {}".format(e))
            
        messages.success(request, "Successfully imported {} employee shift mapping".format(no_of_employee_shift_imported))
    except Exception as e:
        logger.info("unable to import employee shift mapping csv file {}".format(e))
        messages.warning(request, "unable to import employee shift mapping csv file {}".format(e))

    return HttpResponseRedirect(reverse('shifts:employee_shift_list'))