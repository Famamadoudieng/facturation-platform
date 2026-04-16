# paiements/admin.py
from django.contrib import admin
from .models import Paiement

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['numero_paiement', 'facture', 'montant', 'mode_paiement', 'date_paiement', 'statut']
    list_filter = ['mode_paiement', 'statut', 'date_paiement']
    search_fields = ['numero_paiement', 'facture__numero', 'reference']
    readonly_fields = ['numero_paiement', 'created_at', 'updated_at']
    list_editable = ['statut']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('facture', 'numero_paiement')
        }),
        ('Détails du paiement', {
            'fields': ('mode_paiement', 'montant', 'date_paiement', 'reference')
        }),
        ('Statut et notes', {
            'fields': ('statut', 'notes')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )