# config/context_processors.py
from parametres.models import ParametresEntreprise, Entreprise
from django.contrib.auth.models import User

def entreprise_context(request):
    context = {
        'entreprise_nom': 'Facturation Pro',
        'entreprise_logo': None,
    }
    
    # Essayer de récupérer l'entreprise de plusieurs façons
    entreprise_courante = None
    
    # Méthode 1: depuis request
    if hasattr(request, 'entreprise_courante') and request.entreprise_courante:
        entreprise_courante = request.entreprise_courante
    
    # Méthode 2: depuis le profil utilisateur
    elif request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.entreprise:
        entreprise_courante = request.user.profile.entreprise
    
    # Méthode 3: première entreprise de l'utilisateur
    elif request.user.is_authenticated:
        from parametres.models import Entreprise
        entreprises = Entreprise.get_user_entreprises(request.user)
        if entreprises.exists():
            entreprise_courante = entreprises.first()
    
    if entreprise_courante:
        params = ParametresEntreprise.objects.filter(entreprise=entreprise_courante).first()
        if params:
            context['entreprise_nom'] = params.nom_entreprise or entreprise_courante.nom
            context['entreprise_logo'] = params.logo if params.logo else None
        else:
            context['entreprise_nom'] = entreprise_courante.nom
    
    return context