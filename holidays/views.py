from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, reverse
from helpers.web_paginators import *
from .forms import *
from .models import *

import logging
logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
def holiday_list(request):
    """\
    Holiday list with search
    """
    holiday_qs = HolidayCalendar.objects.all().order_by('-created_at')
    query = request.GET.get('search')
    if query:
        holiday_qs = holiday_qs.filter(
            Q(name__icontains=query)
            | Q(day__icontains=query)
            | Q(observance__icontains=query))
    else:
        query = None
    pagination_context = get_fun_pagiantion(request, holiday_qs, 'holidays')
    pagination_context['query'] = query
    return render(request,'holidays/list.html',pagination_context)


@login_required
def holiday_add(request):
    holiday_form = HolidayCreationForm(request.POST or None)
    if request.method == 'POST':
        if holiday_form.is_valid():
            holiday_form.save()
            logger.info("New holidays created")
            messages.success(request, 'Holiday created successfully')
            return HttpResponseRedirect(reverse("holidays:holiday_list"))
    context = {
        'holiday_form':holiday_form
    }
    return render(request=request,
                  template_name="holidays/add.html",
                  context=context)


@login_required
def holiday_edit(request,holiday_id):
    holiday = get_object_or_404(HolidayCalendar, pk=holiday_id)
    holiday_form = HolidayCreationForm(request.POST or None, instance=holiday)
    if request.method == 'POST':
        if holiday_form.is_valid():
            holiday_form.save()
            logger.info("holidays updated")
            messages.success(request, 'Holiday updated successfully')
            return HttpResponseRedirect(reverse("holidays:holiday_list"))
    context = {
        'holiday_form': holiday_form
    }
    return render(request=request,
                  template_name="holidays/edit.html",
                  context=context)
@login_required
def holiday_view(request,holiday_id):
    holiday = get_object_or_404(HolidayCalendar, pk=holiday_id)
    return render(request,"holidays/detail.html",{'holiday':holiday})