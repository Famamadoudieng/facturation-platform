# paiements/urls.py
from django.urls import path
from . import views

app_name = 'paiements'

urlpatterns = [
    path('', views.liste_paiements, name='liste'),  # ✅ Page de liste
    path('facture/<int:facture_pk>/ajouter/', views.ajouter_paiement, name='ajouter'),
    path('<int:pk>/', views.detail_paiement, name='detail'),  # ✅ Détail
    path('<int:pk>/annuler/', views.annuler_paiement, name='annuler'),
    path('<int:pk>/modifier/', views.modifier_paiement, name='modifier'),
        # ✅ Exports
    path('export/csv/', views.exporter_paiements_csv, name='export_csv'),
    path('export/excel/', views.exporter_paiements_excel, name='export_excel'),
    path('export/statistiques/', views.exporter_statistiques_paiements, name='export_statistiques'),

    
]