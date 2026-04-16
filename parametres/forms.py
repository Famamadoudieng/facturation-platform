# parametres/forms.py
from django import forms
from .models import ParametresEntreprise, ParametresFacturation, Entreprise
from django.contrib.auth.models import User
from accounts.models import UserProfile

class ParametresEntrepriseForm(forms.ModelForm):
    """Formulaire pour les paramètres de l'entreprise"""
    class Meta:
        model = ParametresEntreprise
        fields = '__all__'
        exclude = ['id_unique', 'entreprise']
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_3': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_4': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'siret': forms.TextInput(attrs={'class': 'form-control'}),
            'tva_intra': forms.TextInput(attrs={'class': 'form-control'}),
            'capital_social': forms.TextInput(attrs={'class': 'form-control'}),
            'forme_juridique': forms.TextInput(attrs={'class': 'form-control'}),
            'rcs': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
            'bic': forms.TextInput(attrs={'class': 'form-control'}),
            'banque': forms.TextInput(attrs={'class': 'form-control'}),
            'mentions_legales': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'conditions_paiement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pied_page_facture': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ParametresFacturationForm(forms.ModelForm):
    """Formulaire pour les paramètres de facturation"""
    class Meta:
        model = ParametresFacturation
        fields = '__all__'
        exclude = ['id_unique', 'entreprise']
        widgets = {
            'prefixe_facture': forms.TextInput(attrs={'class': 'form-control'}),
            'annee_dans_numero': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'separateur': forms.TextInput(attrs={'class': 'form-control'}),
            'prochain_numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'delai_paiement_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'tva_par_defaut': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'envoyer_email_auto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rappel_paiement_auto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'jours_avant_relance': forms.NumberInput(attrs={'class': 'form-control'}),
            'devise': forms.Select(attrs={'class': 'form-control'}),
        }


class EntrepriseForm(forms.ModelForm):
    """Formulaire pour créer/modifier une entreprise"""
    class Meta:
        model = Entreprise
        fields = ['nom', 'slug']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'entreprise'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'identifiant-unique'}),
        }
        help_texts = {
            'slug': 'Identifiant unique pour l\'URL (ex: mon-entreprise)',
        }
        

# parametres/forms.py


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='Mot de passe')
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label='Confirmer le mot de passe')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise forms.ValidationError('Les mots de passe ne correspondent pas')
        
        return cleaned_data







class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Mot de passe')
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirmer le mot de passe')
    
    # ✅ Ajouter les champs pour les permissions
    is_active = forms.BooleanField(required=False, initial=True, label='Actif', 
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_staff = forms.BooleanField(required=False, initial=False, label='Accès admin', 
                                  widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = UserProfile
        fields = ['role', 'entreprise']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'entreprise': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise forms.ValidationError('Les mots de passe ne correspondent pas')
        
        return cleaned_data