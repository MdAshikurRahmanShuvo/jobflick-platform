from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from jobs.models import Job
from payments.models import WalletTransaction
from payments.services import apply_wallet_transaction


class AdminLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "admin@email.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if not email or not password:
            return cleaned_data
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No user account found for that email.")
        user = authenticate(username=user.username, password=password)
        if not user:
            raise forms.ValidationError("Incorrect email/password combination.")
        if not user.is_staff:
            raise forms.ValidationError("You do not have admin access.")
        cleaned_data["user"] = user
        return cleaned_data


class WalletAdjustmentForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    job = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    direction = forms.ChoiceField(
        choices=WalletTransaction.Direction.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    category = forms.ChoiceField(
        choices=WalletTransaction.Category.choices,
        initial=WalletTransaction.Category.PAYOUT,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    amount = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )
    note = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional note"}),
    )

    def process(self, *, admin_user):
        cleaned = self.cleaned_data
        return apply_wallet_transaction(
            user=cleaned["recipient"],
            amount=cleaned["amount"],
            direction=cleaned["direction"],
            category=cleaned["category"],
            note=cleaned["note"],
            job=cleaned.get("job"),
            initiated_by=admin_user,
        )