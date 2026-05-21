from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from core.models import phone_regex_validator, validate_age_18_plus
from .models import CustomerProfile, User


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
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_age_18_plus],
    )
    phone_number = forms.CharField(
        max_length=20,
        validators=[phone_regex_validator],
        help_text="Format: +375 (29) XXX-XX-XX",
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        return password_confirm


class StaffCreationForm(forms.Form):
    """
    Unified form for creating a new Staff User and their StaffProfile
    simultaneously. Used exclusively by Admins.

    User fields: username, first_name, last_name, email, password,
                 password_confirm.
    StaffProfile fields: position, date_of_birth, contact_details, photo.
    """

    # ---- User account fields ----
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'required': True,
            'minlength': '3',
            'maxlength': '150',
            'autocomplete': 'off',
        }),
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'maxlength': '150'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'maxlength': '150'}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'autocomplete': 'off'}),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'required': True,
            'minlength': '8',
            'autocomplete': 'new-password',
        }),
        help_text="Minimum 8 characters.",
    )
    password_confirm = forms.CharField(
        label="Confirm password",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'required': True,
            'minlength': '8',
            'autocomplete': 'new-password',
        }),
    )

    # ---- StaffProfile fields ----
    position = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'required': True,
            'maxlength': '255',
        }),
    )
    date_of_birth = forms.DateField(
        validators=[validate_age_18_plus],
        widget=forms.DateInput(attrs={
            'type': 'date',
            'required': True,
        }),
        help_text="Staff must be 18 or older.",
    )
    contact_details = forms.CharField(
        widget=forms.Textarea(attrs={
            'required': True,
            'rows': 3,
        }),
        help_text="Phone, email, or other contact information.",
    )
    photo = forms.ImageField(
        required=False,
        help_text="Optional profile photo.",
    )

    # ---- Server-side validation ----

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        return password_confirm
