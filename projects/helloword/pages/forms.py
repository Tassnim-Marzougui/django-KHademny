from django import forms
from .models import Entretien

class EntretienForm(forms.ModelForm):
    class Meta:
        model = Entretien
        fields = ["scheduled_at", "mode", "link_or_address", "notes"]
        widgets = {
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "mode": forms.Select(attrs={"class": "form-select"}),
            "link_or_address": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
