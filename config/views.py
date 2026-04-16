# config/views.py
from django.shortcuts import redirect
from django.contrib.auth import logout

def custom_logout(request):
    """Déconnexion personnalisée"""
    # Supprimer l'entreprise de la session
    if 'entreprise_id' in request.session:
        del request.session['entreprise_id']
    
    # Déconnecter l'utilisateur
    logout(request)
    
    # Rediriger vers une page personnalisée
    return redirect('/parametres/selection/')