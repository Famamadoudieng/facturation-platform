# factures/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Facture, LigneFacture
from produits.models import Produit
from django.utils import timezone
from datetime import timedelta

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['client', 'date_facture', 'date_echeance', 'notes', 'conditions', 'taux_tva']
        # ← Enlève 'statut' des fields
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date_facture': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'taux_tva': forms.Select(attrs={'class': 'form-control'}, choices=Facture.TAUX_TVA_CHOICES),  # ✅ Choix déroulant
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date_facture'].initial = timezone.now().date()
            self.fields['date_echeance'].initial = timezone.now().date() + timedelta(days=30)

class LigneFactureForm(forms.ModelForm):
    class Meta:
        model = LigneFacture
        fields = ['produit', 'designation', 'quantite', 'prix_unitaire_ht']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'value': 1, 'min': 1}),
            'prix_unitaire_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            #'taux_tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 20.0}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.produit_id:
            produit = self.instance.produit
            self.fields['designation'].initial = produit.nom
            #self.fields['prix_unitaire_ht'].initial = produit.prix_ht
            #self.fields['taux_tva'].initial = produit.taux_tva_default

LigneFactureFormSet = inlineformset_factory(
    Facture, 
    LigneFacture, 
    form=LigneFactureForm,
    extra=1, 
    can_delete=True,
    fields=['produit', 'designation', 'quantite', 'prix_unitaire_ht']
)