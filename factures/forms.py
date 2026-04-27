# factures/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Facture, LigneFacture
from produits.models import Produit
from evenements.models import Evenement
from django.utils import timezone
from datetime import timedelta

class FactureForm(forms.ModelForm):
    # ✅ Champ pour sélectionner un événement existant
    evenement = forms.ModelChoiceField(
        queryset=Evenement.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Événement"
    )
    
    # ✅ Champ pour créer un nouvel événement (juste le nom)
    nouvel_evenement = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mariage, Séminaire, Dîner...'}),
        label="Ou créer un nouvel événement"
    )
    
    class Meta:
        model = Facture
        fields = ['client', 'date_facture', 'date_echeance', 'notes', 'conditions', 'taux_tva']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date_facture': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'taux_tva': forms.Select(attrs={'class': 'form-control'}, choices=Facture.TAUX_TVA_CHOICES),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Remplir la liste des événements existants
        if self.request and hasattr(self.request, 'entreprise_courante') and self.request.entreprise_courante:
            self.fields['evenement'].queryset = Evenement.objects.filter(
                entreprise=self.request.entreprise_courante
            ).order_by('-date_debut')
        
        # Valeurs par défaut pour les nouvelles factures
        if not self.instance or not self.instance.pk:
            from datetime import date, timedelta
            self.fields['date_facture'].initial = date.today()
            self.fields['date_echeance'].initial = date.today() + timedelta(days=30)
    
    def clean(self):
        cleaned_data = super().clean()
        evenement = cleaned_data.get('evenement')
        nouvel_evenement = cleaned_data.get('nouvel_evenement')
        
        # Si un nouvel événement est saisi
        if nouvel_evenement:
            if self.request and hasattr(self.request, 'entreprise_courante'):
                # ✅ Créer l'événement directement (sans TypeEvenement)
                nouvel_event = Evenement.objects.create(
                    nom=nouvel_evenement.strip(),
                    client=cleaned_data.get('client'),
                    date_debut=cleaned_data.get('date_facture') or date.today(),
                    entreprise=self.request.entreprise_courante,
                    statut='planifie'
                )
                cleaned_data['evenement'] = nouvel_event
        elif not evenement:
            # Aucun événement sélectionné ni créé
            raise forms.ValidationError("Veuillez sélectionner un événement ou en créer un nouveau.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if hasattr(self, 'cleaned_data') and 'evenement' in self.cleaned_data:
            instance.evenement = self.cleaned_data['evenement']
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


    # partie qui gére la commission
    class Meta:
        model = Facture
        fields = [
            'client', 'date_facture', 'date_echeance', 
            'notes', 'conditions', 'taux_tva',
            'taux_commission', 'commissionnaire', 'commission'  # ✅ Ajouter ces champs
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'date_facture': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'taux_tva': forms.Select(attrs={'class': 'form-control'}, choices=Facture.TAUX_TVA_CHOICES),
            'taux_commission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 10 pour 10%'}),
            'commissionnaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du commissionnaire'}),
            'commission': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Montant fixe'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'taux_commission': 'Taux de commission (%)',
            'commissionnaire': 'Commissionnaire',
            'commission': 'Commission (montant fixe)',
        }
        help_texts = {
            'taux_commission': 'Saisir un taux (ex: 10 pour 10%)',
            'commission': 'Saisir un montant fixe (les deux champs ne sont pas cumulables)',
        }


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.produit_id:
            produit = self.instance.produit
            if produit and not self.instance.designation:
                self.fields['designation'].initial = produit.nom


LigneFactureFormSet = inlineformset_factory(
    Facture, 
    LigneFacture, 
    form=LigneFactureForm,
    extra=1, 
    can_delete=True,
    fields=['produit', 'designation', 'quantite', 'prix_unitaire_ht']
)