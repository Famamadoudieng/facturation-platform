# produits/forms.py
from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        # ✅ Garde seulement les champs qui existent dans ton modèle
        fields = ['nom', 'description']  # Supprime 'code' et 'taux_tva_default'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Description optionnelle'}),
        }
        labels = {
            'nom': 'Nom du produit',
            'description': 'Description',
        }