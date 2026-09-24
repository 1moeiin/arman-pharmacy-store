from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "receiver_full_name",
            "receiver_phone_number",
            "province",
            "city",
            "postal_code",
            "full_address",
            "prescription_image",
        ]
        widgets = {
            "full_address": forms.Textarea(attrs={"rows": 3}),
        }
