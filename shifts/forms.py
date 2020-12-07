from django import forms
from django.contrib.auth import get_user_model
from .models import *


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = "__all__"
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'clockpicker'}),
            'end_time': forms.TimeInput(attrs={'class': 'clockpicker'}),
        }


class BreakForm(forms.ModelForm):
    class Meta:
        model = Break
        fields = "__all__"
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'clockpicker'}),
            'end_time': forms.TimeInput(attrs={'class': 'clockpicker'}),
        }

class EmployeeShiftForm(forms.ModelForm):
    class Meta:
        model = EmployeeShift
        exclude = [
            'employee_attendance',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }