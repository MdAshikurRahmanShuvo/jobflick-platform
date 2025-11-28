from django import forms

from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "work_title",
            "worker_type",
            "duration",
            "amount",
            "location",
            "skills",
        ]
        widgets = {
            "work_title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Web Developer Needed"}),
            "worker_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "Designer, Developer, Electrician"}),
            "duration": forms.TextInput(attrs={"class": "form-control", "placeholder": "3 days, 2 weeks"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "15000"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dhaka, Bangladesh"}),
            "skills": forms.TextInput(attrs={"class": "form-control", "placeholder": "JavaScript, React, UI Design"}),
        }
