from .models import *
from django import forms


class LeaveTypeCreationForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ('name','days')


class FylCreationForm(forms.ModelForm):
    class Meta:
        model = FinancialYearLeaveConfig
        fields = '__all__'


class FylEditForm(forms.ModelForm):
    class Meta:
        model = FinancialYearLeaveConfig
        fields = ('max_leave_carry',)


class LeaveStatusCreationForm(forms.ModelForm):
    class Meta:
        model = LeaveStatus
        fields = ['leave','status','approver','approver_action_at','comments']
        widgets = {
            'approver_action_at': forms.DateInput(attrs={'class': 'datepicker'}),

        }



class FinancialYearCreationForm(forms.ModelForm):
    class Meta:
        model = FinancialYear
        fields = ('start_date','end_date')
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }


class LeaveCreationForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = '__all__'
        widgets = {
            'start_date_at': forms.DateInput(attrs={'class': 'datepicker','autocomplete': 'off'}),
            'end_date_at': forms.DateInput(attrs={'class': 'datepicker','autocomplete': 'off'}),
            'applied_on': forms.DateInput(attrs={'class': 'datepicker','autocomplete': 'off'}),
        }