from accounts.models import *
from departments.models import Department
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from user_type_apps.managers.models import Manager

User = get_user_model()

                
class NewManagerCreationForm(UserCreationForm):
    mobile_number = forms.CharField(max_length=13, required=True)
    code = forms.CharField(max_length=10, label="Manager Code")
    class Meta:
        model = User
        fields = ("code","first_name", "last_name","email", "password1", "password2", 'mobile_number', "is_active",)


class ManagerUpdateForm(forms.ModelForm):
    mobile_number = forms.CharField(max_length=13, required=True)
    code = forms.CharField(max_length=10, label="Manager Code")
    class Meta:
        model = User
        fields = ("code","first_name", "last_name","email", 'mobile_number', "is_active",)

    
class ManagerPasswordChangeForm(forms.Form):
    password1 = forms.CharField(max_length=20, min_length=8, label="Password")
    password2 = forms.CharField(max_length=20, min_length=8, label="Confirm Password")

    def clean(self):
        cleaned_data =  super(ManagerPasswordChangeForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("passwords do not match")
        if password1:
            password_validation.validate_password(password1)
        return cleaned_data


class NewManagerProfileCreationForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ("city",)
        
class ReportToForm(forms.Form):
    report_to = forms.ModelChoiceField(User.objects.exclude(roles__in=[Role.EMPLOYEE, Role.TEAM_LEADER, Role.MANAGER]), label="Report To", help_text="manager default report goes to this user")
    department = forms.ModelChoiceField(Department.objects.all(), label="Department", help_text="Department")

         
# class ManagerModelChoiceField(forms.ModelChoiceField):
#     def label_from_instance(self, obj):
#         return obj.get_full_name()


# class ManagerForm(forms.Form):
#     managers = ManagerModelChoiceField(User.objects.filter(roles__in=[Role.MANAGER]))

#     def __init__(self, *args, **kwargs):
#         super(ManagerForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['class'] = 'form-control'