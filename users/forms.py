from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, CustomerProfile
from core.models import validate_age_18_plus, phone_regex_validator

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                # Also check if it's inactive
                try:
                    user_obj = User.objects.get(username=username)
                    if not user_obj.is_active:
                        raise ValidationError("This user's rights have been revoked.")
                except User.DoesNotExist:
                    pass
                raise ValidationError("Invalid username or password.")
            self.user_cache = user
        return cleaned_data

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    # CustomerProfile fields
    name = forms.CharField(max_length=255, label="Full Name")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), validators=[validate_age_18_plus])
    phone_number = forms.CharField(max_length=20, validators=[phone_regex_validator], help_text="Format: +375 (29) XXX-XX-XX")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        return password_confirm
