from django import forms

from payments.models import WalletTransaction

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "photo",
            "occupation",
            "skills",
            "present_address",
            "bio",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "occupation": forms.TextInput(attrs={"class": "form-control"}),
            "present_address": forms.TextInput(attrs={"class": "form-control"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "e.g. Django, React, Communication"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={"class": "form-control"}))


class WalletPaymentForm(forms.Form):
    amount = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}))
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Describe what this payment is for (optional)",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Enter a positive amount.")
        return amount



class WalletPayoutRequestForm(forms.Form):
    amount = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}))
    note = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Share payout instructions or job reference",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Enter a positive amount.")
        return amount

