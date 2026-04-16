# parametres/admin.py
from django.contrib import admin
from .models import ParametresEntreprise, ParametresFacturation

@admin.register(ParametresEntreprise)
class ParametresEntrepriseAdmin(admin.ModelAdmin):
    list_display = ['nom_entreprise', 'email', 'telephone', 'ville', 'date_modification']
    search_fields = ['nom_entreprise', 'email', 'siret']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom_entreprise', 'slogan', 'logo')
        }),
        ('Images supplémentaires', {
            'fields': ('image_1', 'image_2', 'image_3', 'image_4'),
            'description': 'Images pour le cachet, la signature, etc.'
        }),
        ('Coordonnées', {
            'fields': ('email', 'telephone', 'adresse', 'code_postal', 'ville', 'pays')
        }),
        ('Informations légales', {
            'fields': ('siret', 'tva_intra', 'capital_social', 'forme_juridique', 'rcs'),
            'classes': ('collapse',)
        }),
        ('Coordonnées bancaires', {
            'fields': ('iban', 'bic', 'banque'),
            'classes': ('collapse',)
        }),
        ('Mentions légales et conditions', {
            'fields': ('mentions_legales', 'conditions_paiement', 'pied_page_facture'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Empêche d'ajouter plusieurs instances"""
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression"""
        return False


@admin.register(ParametresFacturation)
class ParametresFacturationAdmin(admin.ModelAdmin):
    list_display = ['prefixe_facture', 'separateur', 'annee_dans_numero', 'prochain_numero', 
                    'delai_paiement_jours', 'tva_par_defaut', 'devise']
    
    fieldsets = (
        ('Numérotation des factures', {
            'fields': ('prefixe_facture', 'separateur', 'annee_dans_numero', 'prochain_numero'),
            'description': 'Exemple: F-2026-0001 (si annee_dans_numero=True) ou F-0001 (sinon)'
        }),
        ('Échéances', {
            'fields': ('delai_paiement_jours',)
        }),
        ('TVA par défaut', {
            'fields': ('tva_par_defaut',)
        }),
        ('Automatisations', {
            'fields': ('envoyer_email_auto', 'rappel_paiement_auto', 'jours_avant_relance'),
            'classes': ('collapse',)
        }),
        ('Devise', {
            'fields': ('devise',)
        }),
    )
    
    def has_add_permission(self, request):
        """Empêche d'ajouter plusieurs instances"""
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression"""
        return False