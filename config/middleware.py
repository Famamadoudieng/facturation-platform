# config/middleware.py
from django.shortcuts import redirect
from parametres.models import Entreprise

class EntrepriseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Vérifier si l'utilisateur a un profil
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                role = profile.role
                
                # ✅ SUPER ADMIN : peut choisir l'entreprise
                if role == 'super_admin':
                    entreprise_id = request.session.get('entreprise_id')
                    if entreprise_id:
                        try:
                            request.entreprise_courante = Entreprise.objects.get(id=entreprise_id)
                        except Entreprise.DoesNotExist:
                            request.entreprise_courante = None
                    else:
                        # Par défaut, première entreprise
                        entreprises = Entreprise.objects.all()
                        if entreprises.exists():
                            request.entreprise_courante = entreprises.first()
                            request.session['entreprise_id'] = request.entreprise_courante.id
                        else:
                            request.entreprise_courante = None
                
                # ✅ ADMIN ENTREPRISE : lié à son entreprise
                elif role == 'admin':
                    if profile.entreprise:
                        request.entreprise_courante = profile.entreprise
                        request.session['entreprise_id'] = profile.entreprise.id
                    else:
                        request.entreprise_courante = None
                
                # ✅ LECTEUR : lié à son entreprise
                elif role == 'lecteur':
                    if profile.entreprise:
                        request.entreprise_courante = profile.entreprise
                        request.session['entreprise_id'] = profile.entreprise.id
                    else:
                        request.entreprise_courante = None
                
                # ✅ AUTRES RÔLES (comptable, commercial)
                else:
                    entreprise_id = request.session.get('entreprise_id')
                    if entreprise_id:
                        try:
                            request.entreprise_courante = Entreprise.objects.get(id=entreprise_id)
                        except Entreprise.DoesNotExist:
                            request.entreprise_courante = None
                    else:
                        if profile.entreprise:
                            request.entreprise_courante = profile.entreprise
                            request.session['entreprise_id'] = profile.entreprise.id
                        else:
                            request.entreprise_courante = None
            else:
                request.entreprise_courante = None
        else:
            request.entreprise_courante = None
        
        response = self.get_response(request)
        return response