from django import forms
from django.contrib.auth import get_user_model
from .models import *


class HolidayCreationForm(forms.ModelForm):
    class Meta:
        model = HolidayCalendar
        fields = ('holiday_on','name','observance')
        widgets = {
            'holiday_on': forms.DateInput(attrs={'class': 'datepicker'}),
        }



