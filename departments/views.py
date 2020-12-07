from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import logging
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, reverse
from helpers.web_paginators import *
from .forms import *
from .models import *

logger = logging.getLogger(__name__)

User = get_user_model()


@login_required
def department_list(request):
    department_qs = Department.objects.all().order_by('-created_at')
    query = request.GET.get('search')
    if query:
        department_qs = department_qs.filter(
            Q(name__icontains=query)
            | Q(organisation__name__icontains=query))
    else:
        query = None
    pagination_context = get_fun_pagiantion(request, department_qs, 'departments')
    pagination_context['query'] = query
    return render(request,'departments/list.html',pagination_context)


@login_required
def department_add(request):
    department_form = DepartmentCreationForm(request.POST or None)
    if request.method == 'POST':
        if department_form.is_valid():
            department_form.save()
            logger.info("New department created")
            messages.success(request, 'department created successfully')
            return HttpResponseRedirect(reverse("departments:department_list"))
    context = {
        'department_form':department_form
    }
    return render(request, 'departments/add.html',context)


@login_required
def department_edit(request,department_id):
    department = get_object_or_404(Department, pk=department_id)
    department_form = DepartmentCreationForm(request.POST or None, instance=department)
    if request.method == 'POST':
        if department_form.is_valid():
            department_form.save()
            logger.info("department updated")
            messages.success(request, 'department updated successfully')
            return HttpResponseRedirect(reverse("departments:department_list"))
    context = {
        'department_form': department_form
    }
    return render(request, 'departments/edit.html',context)


@login_required
def department_view(request,department_id):
    department = get_object_or_404(Department, pk=department_id)
    return render(request,"departments/detail.html",{'department':department})


@login_required
def organisation_list(request):
    organisation_qs = Organisation.objects.all().order_by('-created_at')
    pagination_context = get_fun_pagiantion(request, organisation_qs, 'organisations')
    return render(request,'departments/organisation/list.html',pagination_context)

@login_required
def organisation_view(request,organisation_id):
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    return render(request,"departments/organisation/detail.html",{'organisation':organisation})

@login_required
def organisation_edit(request,organisation_id):
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    organisation_form = OrganisationCreationForm(request.POST or None, instance=organisation)
    if request.method == 'POST':
        if organisation_form.is_valid():
            organisation_form.save()
            logger.info("organisation updated")
            messages.success(request, 'organisation updated successfully')
            return HttpResponseRedirect(reverse("departments:organisation_list"))
    context = {
        'organisation_form': organisation_form
    }
    return render(request, 'departments/organisation/edit.html',context)