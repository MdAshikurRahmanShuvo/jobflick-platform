from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Transaction


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


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["recipient", "job", "amount", "note"]
        widgets = {
            "recipient": forms.Select(attrs={"class": "form-control"}),
            "job": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "note": forms.TextInput(attrs={"class": "form-control", "placeholder": "Payment details"}),
        }