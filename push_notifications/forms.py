from django import forms
from .models import *


class FcmSettingForm(forms.ModelForm):
    
    class Meta:
        model = FcmSetting
        fields = ("api_key",)