from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import Address, User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["phone_number", "first_name", "last_name", "email"]

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("این شماره موبایل قبلاً ثبت‌نام کرده است.")
        return phone_number


class PhoneAuthenticationForm(AuthenticationForm):
    """AuthenticationForm already reads USERNAME_FIELD, so the first field
    is phone_number automatically — we only relabel it for the template."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "شماره موبایل یا رمز عبور اشتباه است.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "شماره موبایل"
        self.fields["username"].widget.attrs.update({"autocomplete": "tel", "placeholder": "09XXXXXXXXX"})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "national_id"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ["user", "created_at"]
        widgets = {
            "full_address": forms.Textarea(attrs={"rows": 3}),
        }
