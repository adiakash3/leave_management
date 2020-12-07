import math
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from django.shortcuts import render, reverse
from django.shortcuts import get_object_or_404, redirect, HttpResponseRedirect
from .models import *
from .forms import *
from .otp_generate import *

import logging
from emails.utils.emails import BaseEmail

logger = logging.getLogger(__name__)


def login_request(request):
    """ login user """
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if not user.roles.filter(id__in=[Role.ADMIN, Role.MANAGER, Role.TEAM_LEADER]).exists():
                messages.warning(request, 'Only Admin, Manger, Team leader can login here')
                return render(request, 'accounts/login.html', {'form': form})
            if user is not None:
                login(request, user)
                next = request.GET.get('next')
                if next:
                    return redirect(next)
                return HttpResponseRedirect(reverse('dashboard:home'))

            else:
                messages.error(request, "Invalid username or password.")
        else:
            return render(request, 'accounts/login.html', {'form': form})
    form = AuthenticationForm()
    return render(request=request, template_name="accounts/login.html", context={"form": form})


@login_required
def logout_request(request):
    """ logout user """
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("accounts:main_login")


def forgot_password(request):
    """ if user request new password or change password using mobile number """
    form = EmailPostForm(request.POST or None)
    if request.method == 'POST':
        email_id = request.POST['Email_form']
        if User.objects.filter(email=email_id).exists():
            user = User.objects.get(email=email_id)
            try:
                # email
                otp = generate_otp()
                message = "Hi, this is msg from leave management to change password and verification code is {} for username '{}'".format(
                    otp, user.username)

                mail_dict = {
                    'subject': "Password Reset",
                    'plain_message': message,
                    'recipient_list': ['{}'.format(user.email)],
                }
                BaseEmail.send_mail(**mail_dict)
            except Exception as e:
                messages.error(request, "error while sending OTP {}".format(e))
                return render(request=request,
                              template_name="accounts/forgot_password/reset_password.html",
                              context={"form": form})

            EmailOtp.objects.create(
                otp=otp,
                email=email_id
            )
            messages.info(request, "OTP sent to Email {} ".format(email_id))
            return HttpResponseRedirect(reverse("accounts:main_forgot_password_otp_verify"))
        else:
            messages.error(request, "{} Email does not match our records".format(email_id))
            return render(request=request,
                          template_name="accounts/forgot_password/reset_password.html",
                          context={"email_id": email_id})

    form = EmailPostForm()
    return render(request=request, template_name="accounts/forgot_password/reset_password.html", context={"form": form})


def forgot_password_otp_verify(request):
    """ Emaile verification for new password """
    if request.method == "POST":
        form = EmailOtpForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            if EmailOtp.objects.filter(otp=otp).exists():
                email_id = EmailOtp.objects.get(otp=otp).email
                EmailOtp.objects.get(otp=otp).delete()
                messages.info(request, "Your otp has been verified successfully")
                return HttpResponseRedirect(
                    reverse("accounts:main_new_password", kwargs={"email_id": email_id}))
            messages.error(request, "Entered otp is invalid")
            return render(request=request, template_name="accounts/forgot_password/otp_verify.html",
                          context={"form": form, })

        return render(request=request, template_name="accounts/forgot_password/otp_verify.html",
                      context={"form": form})

    return render(request=request, template_name="accounts/forgot_password/otp_verify.html")


def new_password(request, email_id):
    if request.method == "POST":
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password1')
            user = User.objects.get(email=email_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Your Password successfully changed please login to continue')
            return redirect("accounts:main_login")
        return render(request=request, template_name="accounts/forgot_password/new_password.html",
                      context={"form": form})
    form = NewPasswordForm()
    return render(request=request, template_name="accounts/forgot_password/new_password.html",
                  context={"form": form})


@login_required
def profile(request):
    admin_profile = request.user
    profile = Profile.objects.get(user=request.user)
    profile_data = {
        'username': admin_profile.username,
        'profile_photo': profile,
        'first_name': admin_profile.first_name,
        'last_name': admin_profile.last_name,
        'email': admin_profile.email,
        'mobile_number': admin_profile.mobile_number,
        'profile_address': profile.address,
        'profile_pin': profile.pincode,
        'profile_city': profile.city,
    }
    return render(request, 'profile/profile.html', profile_data)


def edit_profile(request):
    user = request.user
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        profile.address = request.POST['address']
        profile.city = request.POST['city']
        profile.pincode = request.POST['pincode']
        profile.save()
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.mobile_number = request.POST['mobile_number']
        user.email = request.POST['email']
        user.save()

        if request.FILES:
            profile.image = request.FILES['profile_image']
            profile.updated_by = request.user
            profile.save()

        messages.success(request, 'Profile updated successfully!')
        return HttpResponseRedirect(reverse('accounts:profile'))

    context = {
        'profile_address': profile.address,
        'profile_pin': profile.pincode,
        'profile_city': profile.city,
        'edit_profile': user,
        'mobile': request.user.mobile_number,
    }
    return render(request, 'profile/edit_profile.html', context)


def verify_otp_with_email(request):
    """ OTP verification while email """

    if request.method == "POST":
        form = EmailOtpForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            if EmailOtp.objects.get(otp=otp).delete():
                messages.info(request, "Your otp has been verified and changed successfully!")
                return HttpResponseRedirect(reverse("accounts:accounts:profile"))
            else:
                messages.error(request, "Entered otp is invalid")
                return render(request=request,
                              template_name="accounts/otp_verify_email.html",
                              context={"form": form})
        else:
            return render(request=request,
                          template_name="accounts/otp_verify_email.html",
                          context={"form": form})

    form = EmailPostForm()
    return render(request=request,
                  template_name="accounts/otp_verify_email.html",
                  context={"form": form})


def change_password(request):
    logged_in_user = request.user
    if request.method == 'POST':
        if check_password(request.POST['old_password'], logged_in_user.password):
            if check_password(request.POST['new_password'], logged_in_user.password):
                messages.error(request, 'New password is same as old password!')
                return HttpResponseRedirect(reverse('change_password'))
            if request.POST['new_password'] == request.POST['confirm_password']:
                logged_in_user.set_password(request.POST['new_password'])
                logged_in_user.save()
                messages.success(request, 'Password changed successfully, you can login with new login password!')
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'New password & Confirm password mismatched')
                return HttpResponseRedirect(reverse('change_password'))
        else:
            messages.error(request, 'Old password is wrong')
            return HttpResponseRedirect(reverse('change_password'))

    return render(request, 'profile/change_password.html')
