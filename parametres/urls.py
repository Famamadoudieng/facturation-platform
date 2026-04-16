# parametres/urls.py
from django.urls import path
from . import views

app_name = 'parametres'

urlpatterns = [
    path('', views.parametres_index, name='index'),
    path('entreprise/', views.parametres_entreprise, name='entreprise'),
    path('facturation/', views.parametres_facturation, name='facturation'),
    path('supprimer-image/<str:image_type>/', views.supprimer_image, name='supprimer_image'),

        # ✅ NOUVELLES URLs pour multi-entreprises
    path('selection/', views.selection_entreprise, name='selection_entreprise'),
    path('creer/', views.creer_entreprise, name='creer_entreprise'),
    path('changer/<int:entreprise_id>/', views.changer_entreprise, name='changer_entreprise'),
    path('liste/', views.entreprise_liste, name='entreprise_list'),
    #path('modifier/<int:pk>/', views.entreprise_modifier, name='entreprise_modifier'),
    path('entreprises/<int:pk>/modifier/', views.entreprise_modifier, name='entreprise_modifier'),  # ✅ Ajouter cette ligne

    # Gestion des utilisateurs
    path('utilisateurs/', views.utilisateur_liste, name='utilisateur_liste'),
    path('utilisateurs/creer/', views.utilisateur_creer, name='utilisateur_creer'),
    path('utilisateurs/<int:pk>/modifier/', views.utilisateur_modifier, name='utilisateur_modifier'),
    path('utilisateurs/<int:pk>/supprimer/', views.utilisateur_supprimer, name='utilisateur_supprimer'),

    # Gestion des profils utilisateurs
    path('profils/', views.profil_liste, name='profil_liste'),
    path('profils/creer/', views.profil_creer, name='profil_creer'),
    path('profils/<int:pk>/modifier/', views.profil_modifier, name='profil_modifier'),
    path('profils/<int:pk>/supprimer/', views.profil_supprimer, name='profil_supprimer'),


]