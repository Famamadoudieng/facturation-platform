from django.contrib import admin
from .models import Evenement

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'client', 'date_debut', 'date_fin', 'statut']
    list_filter = ['statut', 'nom']
    search_fields = ['nom', 'client__nom']