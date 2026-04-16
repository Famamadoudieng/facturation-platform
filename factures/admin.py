from django.contrib import admin

# Register your models here.
# factures/admin.py
from django.contrib import admin
from .models import Facture, LigneFacture

class LigneFactureInline(admin.TabularInline):
    """Affiche les lignes de facture directement dans la page de la facture"""
    model = LigneFacture
    extra = 1
    fields = ['produit', 'designation', 'quantite', 'prix_unitaire_ht', 'taux_tva']
    raw_id_fields = ['produit']
    show_change_link = True

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'date_facture', 'date_echeance', 'type_facture', 'statut', 'est_archive', 'total_ttc_admin']
    list_filter = ['type_facture', 'statut', 'est_archive', 'date_facture', 'date_creation']
    search_fields = ['numero', 'client__nom', 'client__email']
    readonly_fields = ['date_creation', 'created_at', 'updated_at', 'total_ht_admin', 'total_tva_admin', 'total_ttc_admin']
    inlines = [LigneFactureInline]
    list_per_page = 20
    date_hierarchy = 'date_facture'
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('numero', 'client', 'type_facture', 'statut')
        }),
        ('Dates', {
            'fields': ('date_facture', 'date_echeance', 'date_creation')
        }),
        ('Totaux (calculés automatiquement)', {
            'fields': ('total_ht_admin', 'total_tva_admin', 'total_ttc_admin'),
            'classes': ('collapse',)
        }),
        ('Notes et conditions', {
            'fields': ('conditions', 'notes'),
            'classes': ('collapse',)
        }),
        ('Archive', {
            'fields': ('est_archive',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_ht_admin(self, obj):
        return f"{obj.total_ht:,.2f} €"
    total_ht_admin.short_description = "Total HT"
    
    def total_tva_admin(self, obj):
        return f"{obj.total_tva:,.2f} €"
    total_tva_admin.short_description = "Total TVA"
    
    def total_ttc_admin(self, obj):
        return f"{obj.total_ttc:,.2f} €"
    total_ttc_admin.short_description = "Total TTC"
    
    def get_queryset(self, request):
        """Optimise les requêtes pour l'admin"""
        return super().get_queryset(request).prefetch_related('lignes', 'client')
    
    actions = ['archiver_factures', 'desarchiver_factures', 'marquer_payees']
    
    def archiver_factures(self, request, queryset):
        queryset.update(est_archive=True)
        self.message_user(request, f"{queryset.count()} facture(s) archivée(s).")
    archiver_factures.short_description = "Archiver les factures sélectionnées"
    
    def desarchiver_factures(self, request, queryset):
        queryset.update(est_archive=False)
        self.message_user(request, f"{queryset.count()} facture(s) désarchivée(s).")
    desarchiver_factures.short_description = "Désarchiver les factures sélectionnées"
    
    def marquer_payees(self, request, queryset):
        queryset.update(statut='payee')
        self.message_user(request, f"{queryset.count()} facture(s) marquée(s) comme payée(s).")
    marquer_payees.short_description = "Marquer comme payées"


@admin.register(LigneFacture)
class LigneFactureAdmin(admin.ModelAdmin):
    list_display = ['facture', 'designation', 'quantite', 'prix_unitaire_ht', 'total_ht_admin']
    list_filter = ['facture__statut']
    search_fields = ['designation', 'facture__numero']
    raw_id_fields = ['facture', 'produit']
    list_select_related = ['facture', 'produit']
    
    def total_ht_admin(self, obj):
        return f"{obj.total_ht:,.2f} €"
    total_ht_admin.short_description = "Total HT"