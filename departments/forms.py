from django import forms
from django.contrib.auth import get_user_model
from .models import *


class DepartmentCreationForm(forms.ModelForm):
    organisation = forms.ModelChoiceField(queryset=Organisation.objects.all(),label="Organisation")
    name = forms.CharField(required=True)
    class Meta:
        model = Department
        fields = ('name','organisation')

class OrganisationCreationForm(forms.ModelForm):
    name = forms.CharField(required=True)
    class Meta:
        model = Organisation
        fields = ('name','location')
