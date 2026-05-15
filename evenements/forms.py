from django import forms
from .models import Evenement

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = [
            'nom', 'client', 'date_debut', 'date_fin', 'date_arrivee', 'date_depart',
            'heure_debut', 'heure_fin', 'lieu', 'nombre_personnes',
            'statut', 'notes'#, 'entreprise'
        ]
        widgets = {
            'nom': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_arrivee': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_depart': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_personnes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            #'entreprise': forms.Select(attrs={'class': 'form-select'}),
        }