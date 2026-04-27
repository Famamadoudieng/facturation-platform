# evenements/forms.py
from django import forms
from .models import Evenement

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = [
            'nom', 'client', 'date_debut', 'date_fin',
            'heure_debut', 'heure_fin', 'lieu', 'nombre_personnes',
            'statut', 'notes'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mariage, Séminaire...'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du lieu'}),
            'nombre_personnes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            #'budget_prevu': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Notes supplémentaires'}),
        }
        labels = {
            'nom': 'Nom de l\'événement',
            'client': 'Client',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'heure_debut': 'Heure de début',
            'heure_fin': 'Heure de fin',
            'lieu': 'Lieu',
            'nombre_personnes': 'Nombre de personnes',
            #'budget_prevu': 'Budget prévu (FCFA)',
            'statut': 'Statut',
            'notes': 'Notes',
        }
        help_texts = {
            'date_fin': 'Optionnel',
            'heure_debut': 'Optionnel',
            'heure_fin': 'Optionnel',
            'lieu': 'Optionnel',
            'notes': 'Informations supplémentaires',
        }