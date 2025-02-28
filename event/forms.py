from django import forms
from .models import Event, Category

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'image', 'location', 'start_date', 'end_date', 
                 'capacity', 'price', 'category', 'is_public']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'is_public': 'Événement public',
            'title': 'Titre',
            'description': 'Description',
            'image': 'Image',
            'location': 'Lieu',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'capacity': 'Capacité',
            'price': 'Prix (laissez vide pour gratuit)',
            'category': 'Catégorie'
        }
        help_texts = {
            'is_public': 'Décochez pour créer un événement privé avec un lien unique',
        }
