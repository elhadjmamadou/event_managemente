from django import forms
from .models import Event, Category

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'image', 'location', 'start_date', 'end_date', 'capacity', 'price', 'category']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'})
        }
