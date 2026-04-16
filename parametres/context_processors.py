# config/context_processors.py
from parametres.models import ParametresEntreprise

def entreprise_context(request):
    """Context processor pour ajouter les infos de l'entreprise à tous les templates"""
    context = {
        'entreprise_nom': 'Mon Entreprise',
        'entreprise_logo': None,
    }
    
    if hasattr(request, 'entreprise_courante') and request.entreprise_courante:
        try:
            # Récupérer les paramètres de l'entreprise courante
            params = ParametresEntreprise.objects.filter(entreprise=request.entreprise_courante).first()
            if params:
                context['entreprise_nom'] = params.nom_entreprise or request.entreprise_courante.nom
                if params.logo and params.logo.url:
                    context['entreprise_logo'] = params.logo
            else:
                context['entreprise_nom'] = request.entreprise_courante.nom
        except Exception as e:
            print(f"Erreur context processor: {e}")
            context['entreprise_nom'] = request.entreprise_courante.nom
    
    return context