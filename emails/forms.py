from django import forms
from django.contrib.auth import get_user_model
from .models import *


class MailForm(forms.ModelForm):
    class Meta:
        model = Mail
        fields = ['subject', 'body']

