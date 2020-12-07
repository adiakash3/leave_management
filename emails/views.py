from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, reverse
from helpers.web_paginators import *

# Create your views here.


@login_required
def add_mail(request):
    """
    Add mail using key
    """
    if request.method == 'POST':
        mail_form = MailForm(request.POST)
        if mail_form.is_valid():
            mail_form.save()
            messages.success(request, 'Mail added successfully')
            return HttpResponseRedirect(reverse('emails:mail_list'))
    else:
        mail_form = MailForm()
    context = {
        'form': mail_form
    }
    return render(request, 'email/add.html', context)

@login_required
def mail_list(request):
    mail_qs = Mail.objects.all().order_by('-created_at')
    pagination_context = get_fun_pagiantion(request, mail_qs, 'mails')
    return render(request, 'email/list.html', pagination_context)