from django import forms
from leaves.models import EmployeeFYL, FinancialYear, LeaveType

class DaysForm(forms.Form):
    DAY_CHOICES = (
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    )
    day =  forms.ChoiceField(choices=DAY_CHOICES, required=False, label = "This week employees report")
    
    
class FinancialYearForm(forms.Form):
    year = forms.ModelChoiceField(FinancialYear.objects.all(),label="Financial Year",)
    
    def __init__(self, *args, **kwargs):
        super(FinancialYearForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'custom-select'
            
            
class LeaveCarryForm(forms.ModelForm):
    leave_type = forms.ModelChoiceField(LeaveType.objects.all(),label="Leave type", required=False)
    class Meta:
        model = EmployeeFYL
        fields = ['leave_type', 'carried_leave_no', 'comment']
        
    def __init__(self, *args, **kwargs):
        super(LeaveCarryForm, self).__init__(*args, **kwargs)
        self.fields['leave_type'].widget.attrs['disabled'] = True 
        