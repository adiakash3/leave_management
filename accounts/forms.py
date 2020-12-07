from accounts.models import *
from django import forms


# creating a form
class EmailPostForm(forms.Form):
    email = forms.EmailField(max_length=200)


class EmailOtpForm(forms.ModelForm):
    class Meta:
        model = EmailOtp
        fields = ['otp']


class NewPasswordForm(forms.Form):
    password1 = forms.CharField(max_length=20, min_length=8)
    password2 = forms.CharField(max_length=20, min_length=8)

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("passwords do not match")
