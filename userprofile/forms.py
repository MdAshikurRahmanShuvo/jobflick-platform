from django import forms
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
