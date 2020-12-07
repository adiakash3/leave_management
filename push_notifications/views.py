from django.contrib import messages
from django.contrib.auth.decorators import *
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, reverse
from .models import *
from .forms import *

@login_required
def push_notification_add(request):
    """
    Add fcm api key
    """
    fcm_setting, is_created = FcmSetting.objects.get_or_create(id=1)
    fcm_setting_form = FcmSettingForm(request.POST or None, instance=fcm_setting)
    if request.method == "POST":
        if fcm_setting_form.is_valid():
            fcm_setting_form.save()
            messages.success(request, "FCM server API key successfully updated")
            return HttpResponseRedirect(reverse('push_notifications:push_notification_view'))
    
    context = {
        "fcm_setting_form":fcm_setting_form
    }
    return render(request, 'push_notifications/add.html', context)


@login_required
def push_notification_view(request):
    """
    view fcm api key
    """
    fcm_setting, is_created = FcmSetting.objects.get_or_create(id=1)
    context = {
        "fcm_setting":fcm_setting
    }
    return render(request, 'push_notifications/view.html', context)