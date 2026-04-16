
from django.urls import path
from . import views
from . import views_pdf
from .exports import export_comptabilite

app_name = 'factures'

urlpatterns = [
    path('', views.FactureListView.as_view(), name='list'),
    path('ajouter/', views.FactureCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FactureDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.FactureUpdateView.as_view(), name='update'),
    path('<int:pk>/modifier/', views.FactureUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.FactureDeleteView.as_view(), name='delete'),
    path('<int:pk>/ajouter-produit/', views.ajouter_produit, name='ajouter_produit'),
    path('ligne/<int:pk>/supprimer/', views.supprimer_ligne, name='supprimer_ligne'),
    #path('<int:pk>/pdf/', views_pdf.FacturePDF, name='pdf'),
    path('<int:pk>/pdf/', views_pdf.generer_pdf_facture, name='pdf'),
        # Nouvelles URLs pour la gestion des statuts
    path('<int:pk>/finaliser/', views.finaliser_facture, name='finaliser'),
    path('<int:pk>/annuler/', views.annuler_facture, name='annuler'),
    path('<int:pk>/envoyer/', views.marquer_envoyee, name='envoyer'),
    path('<int:pk>/payer/', views.marquer_payee, name='payer'),
    path('<int:pk>/impayer/', views.marquer_impayee, name='impayer'),
    path('<int:pk>/telecharger/', views_pdf.telecharger_pdf_facture, name='telecharger'),
    path('<int:pk>/archiver/', views.archiver_facture, name='archiver'),
    path('<int:pk>/desarchiver/', views.desarchiver_facture, name='desarchiver'), 
        # Exports
    path('export/csv/', views.exporter_factures_csv, name='export_csv'),
    path('export/excel/', views.exporter_factures_excel, name='export_excel'),
    path('export/statistiques/', views.exporter_statistiques_excel, name='export_statistiques'),
    path('export/comptabilite/', export_comptabilite, name='export_comptabilite'),
]
