from django import forms
from django.contrib.auth import UserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import MyUser

class RegistratinForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ("phone","password","user_category","email","age","address","first_name","middle_name","last_name","gender","food_preference")
    
    def clean(self):
        '''
        Verify both passwords match.
        '''
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 is not None and password1 != password2:
            self.add_error("password2", "Your passwords must match")
        return cleaned_data

    def clean_email(self):
        '''
        Verify email is available.
        '''
        email = self.cleaned_data.get('email')
        qs = MyUser.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_phone(self):
        '''
        Verify email is available.
        '''
        phone = self.cleaned_data.get('phone')
        qs = MyUser.objects.filter(phone=phone)
        if qs.exists():
            raise forms.ValidationError("This phone number has already been taken")
        return phone