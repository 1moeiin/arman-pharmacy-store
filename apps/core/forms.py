from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone_number", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "نام و نام خانوادگی", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "ایمیل", "autocomplete": "email"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "شماره تماس", "autocomplete": "tel"}),
            "message": forms.Textarea(attrs={"placeholder": "پیام شما", "rows": 5}),
        }
