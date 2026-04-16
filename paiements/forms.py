# paiements/forms.py
from django import forms
from .models import Paiement
from factures.models import Facture

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['mode_paiement', 'montant', 'date_paiement', 'reference', 'notes']
        widgets = {
            'mode_paiement': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_paiement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° chèque, transaction...'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.facture = kwargs.pop('facture', None)
        super().__init__(*args, **kwargs)
        
        if self.facture:
            reste_a_payer = self.facture.total_ttc - self.facture.total_paye
            self.fields['montant'].help_text = f"Montant restant à payer: {reste_a_payer:,.2f} FCFA"
            self.fields['montant'].max_value = reste_a_payer
    
    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if self.facture:
            reste = self.facture.total_ttc - self.facture.total_paye
            if montant > reste:
                raise forms.ValidationError(f"Le montant ne peut pas dépasser le reste à payer ({reste:,.2f} FCFA)")
        return montant