# factures/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Facture, LigneFacture
from produits.models import Produit
from evenements.models import Evenement
from django.utils import timezone
from datetime import timedelta
from datetime import date, timedelta

class FactureForm(forms.ModelForm):
    # ✅ Types d'événements prédéfinis (liste déroulante)
    type_evenement = forms.ChoiceField(
        choices=Evenement.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Type d'événement"
    )
    
    class Meta:
        model = Facture
        fields = [
            'client', 'date_facture', 'date_echeance', 'date_arrivee', 'date_depart',
            'notes', 'conditions', 'taux_tva',
            'taux_commission', 'commissionnaire', 'commission'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date_facture': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_arrivee': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_depart': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'taux_tva': forms.Select(attrs={'class': 'form-control'}, choices=Facture.TAUX_TVA_CHOICES),
            'taux_commission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'commissionnaire': forms.TextInput(attrs={'class': 'form-control'}),
            'commission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Valeurs par défaut
        if not self.instance or not self.instance.pk:
        #if not self.instance.pk:
            
            self.fields['date_facture'].initial = date.today()
            self.fields['date_echeance'].initial = date.today() + timedelta(days=30)
            

    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # ✅ Créer automatiquement l'événement à partir du type sélectionné
        type_evenement = self.cleaned_data.get('type_evenement')
        if type_evenement and self.request and hasattr(self.request, 'entreprise_courante'):
            # Créer ou récupérer l'événement
            evenement, created = Evenement.objects.get_or_create(
                nom=type_evenement,
                client=instance.client,
                date_debut=instance.date_facture,
                entreprise=self.request.entreprise_courante,
                defaults={'statut': 'planifie'}
            )
            instance.evenement = evenement
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class LigneFactureForm(forms.ModelForm):
    class Meta:
        model = LigneFacture
        fields = ['produit', 'designation', 'quantite', 'prix_unitaire_ht']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'value': 1, 'min': 1}),
            'prix_unitaire_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            
        }


LigneFactureFormSet = inlineformset_factory(
    Facture, 
    LigneFacture, 
    form=LigneFactureForm,
    extra=0, 
    can_delete=True,
    fields=['produit', 'designation', 'quantite', 'prix_unitaire_ht']
)