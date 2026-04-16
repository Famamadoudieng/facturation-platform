# produits/admin.py
from django.contrib import admin
from .models import Produit

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description_courte', 'date_ajout']
    list_display_links = ['nom']
    search_fields = ['nom', 'description']
    
    readonly_fields = ['date_ajout']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description')
        }),
        ('Informations système', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )
    
    def description_courte(self, obj):
        """Affiche les 50 premiers caractères de la description"""
        if obj.description:
            return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
        return '-'
    description_courte.short_description = "Description"
    
    def date_ajout(self, obj):
        """Affiche la date d'ajout (basée sur l'ID ou ajouter un champ)"""
        # Note: Sans champ date_creation, on peut utiliser l'ID comme proxy
        return f"ID: {obj.id}"
    date_ajout.short_description = "Référence"
    
    actions = ['supprimer_selection']
    
    def supprimer_selection(self, request, queryset):
        """Action personnalisée pour supprimer en masse"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} produit(s) supprimé(s) avec succès.")
    supprimer_selection.short_description = "Supprimer définitivement la sélection"