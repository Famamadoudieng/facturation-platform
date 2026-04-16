# parametres/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from .models import ParametresEntreprise, ParametresFacturation, Entreprise
from .forms import ParametresEntrepriseForm, ParametresFacturationForm, EntrepriseForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import UserForm
from accounts.models import UserProfile
from accounts.forms import UserProfileForm
from parametres.forms import UserProfileForm

# ============================================
# PARAMÈTRES (accès restreint aux staff)
# ============================================

@staff_member_required
def parametres_index(request):
    """Page d'accueil des paramètres"""
    return render(request, 'parametres/index.html')


@staff_member_required
def parametres_entreprise(request):
    """Vue pour modifier les paramètres de l'entreprise"""
    # ✅ Récupérer l'entreprise courante
    entreprise_courante = request.entreprise_courante
    instance = ParametresEntreprise.get_instance(entreprise_courante)
    
    if request.method == 'POST':
        # Informations générales
        instance.nom_entreprise = request.POST.get('nom_entreprise')
        instance.slogan = request.POST.get('slogan')
        
        # Gestion du logo
        if request.FILES.get('logo'):
            instance.logo = request.FILES['logo']
        
        # Gestion des images supplémentaires
        if request.FILES.get('image_1'):
            instance.image_1 = request.FILES['image_1']
        if request.FILES.get('image_2'):
            instance.image_2 = request.FILES['image_2']
        if request.FILES.get('image_3'):
            instance.image_3 = request.FILES['image_3']
        if request.FILES.get('image_4'):
            instance.image_4 = request.FILES['image_4']
        
        # Coordonnées
        instance.email = request.POST.get('email')
        instance.telephone = request.POST.get('telephone')
        instance.adresse = request.POST.get('adresse')
        instance.code_postal = request.POST.get('code_postal')
        instance.ville = request.POST.get('ville')
        instance.pays = request.POST.get('pays')
        
        # Informations légales
        instance.siret = request.POST.get('siret')
        instance.tva_intra = request.POST.get('tva_intra')
        instance.capital_social = request.POST.get('capital_social')
        instance.forme_juridique = request.POST.get('forme_juridique')
        instance.rcs = request.POST.get('rcs')
        
        # Banque
        instance.iban = request.POST.get('iban')
        instance.bic = request.POST.get('bic')
        instance.banque = request.POST.get('banque')
        
        # Mentions
        instance.mentions_legales = request.POST.get('mentions_legales')
        instance.conditions_paiement = request.POST.get('conditions_paiement')
        instance.pied_page_facture = request.POST.get('pied_page_facture')
        
        instance.save()
        messages.success(request, 'Paramètres de l\'entreprise mis à jour avec succès !')
        return redirect('parametres:entreprise')
    
    context = {'entreprise': instance}
    return render(request, 'parametres/entreprise.html', context)


@staff_member_required
def parametres_facturation(request):
    """Vue pour modifier les paramètres de facturation"""
    # ✅ Récupérer l'entreprise courante
    entreprise_courante = request.entreprise_courante
    instance = ParametresFacturation.get_instance(entreprise_courante)
    
    if request.method == 'POST':
        instance.prefixe_facture = request.POST.get('prefixe_facture')
        instance.annee_dans_numero = request.POST.get('annee_dans_numero') == 'on'
        instance.separateur = request.POST.get('separateur')
        instance.prochain_numero = request.POST.get('prochain_numero')
        instance.delai_paiement_jours = request.POST.get('delai_paiement_jours')
        instance.tva_par_defaut = request.POST.get('tva_par_defaut')
        instance.envoyer_email_auto = request.POST.get('envoyer_email_auto') == 'on'
        instance.rappel_paiement_auto = request.POST.get('rappel_paiement_auto') == 'on'
        instance.jours_avant_relance = request.POST.get('jours_avant_relance')
        instance.devise = request.POST.get('devise')
        
        instance.save()
        messages.success(request, 'Paramètres de facturation mis à jour avec succès !')
        return redirect('parametres:facturation')
    
    context = {'facturation': instance}
    return render(request, 'parametres/facturation.html', context)


@staff_member_required
def supprimer_image(request, image_type):
    """Supprimer une image spécifique"""
    # ✅ Récupérer l'entreprise courante
    entreprise_courante = request.entreprise_courante
    instance = ParametresEntreprise.get_instance(entreprise_courante)
    
    if image_type == 'logo':
        if instance.logo:
            instance.logo.delete()
            instance.logo = None
    elif image_type == 'image_1':
        if instance.image_1:
            instance.image_1.delete()
            instance.image_1 = None
    elif image_type == 'image_2':
        if instance.image_2:
            instance.image_2.delete()
            instance.image_2 = None
    elif image_type == 'image_3':
        if instance.image_3:
            instance.image_3.delete()
            instance.image_3 = None
    elif image_type == 'image_4':
        if instance.image_4:
            instance.image_4.delete()
            instance.image_4 = None
    
    instance.save()
    messages.success(request, 'Image supprimée avec succès !')
    return redirect('parametres:entreprise')


# ============================================
# MULTI-ENTREPRISES
# ============================================


@login_required
def selection_entreprise(request):
    """Page de sélection d'entreprise"""
    # ✅ Si l'utilisateur est lecteur, rediriger directement
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur' or request.user.profile.role == 'comptable':
        if request.user.profile.entreprise:
            request.session['entreprise_id'] = request.user.profile.entreprise.id
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Vous n\'êtes pas associé à une entreprise')
            return redirect('logout')
    
    entreprises = Entreprise.get_user_entreprises(request.user)
    
    if request.method == 'POST':
        entreprise_id = request.POST.get('entreprise_id')
        if entreprise_id:
            try:
                entreprise = entreprises.get(id=entreprise_id)
                request.session['entreprise_id'] = entreprise.id
                messages.success(request, f'Bienvenue sur {entreprise.nom}')
                return redirect('/dashboard/')
            except Entreprise.DoesNotExist:
                messages.error(request, 'Entreprise non trouvée')
    
    return render(request, 'parametres/selection_entreprise.html', {
        'entreprises': entreprises
    })


# parametres/views.py
@login_required
def creer_entreprise(request):
    """Créer une nouvelle entreprise"""
    if request.method == 'POST':
        form = EntrepriseForm(request.POST)
        if form.is_valid():
            entreprise = form.save(commit=False)
            entreprise.proprietaire = request.user  # ✅ Lier à l'utilisateur connecté
            entreprise.save()
            entreprise.utilisateurs.add(request.user)
            
            # Créer les paramètres par défaut
            ParametresEntreprise.objects.create(
                entreprise=entreprise,
                nom_entreprise=entreprise.nom
            )
            ParametresFacturation.objects.create(
                entreprise=entreprise,
                prefixe_facture='FACT',
                devise='XOF'
            )
            
            request.session['entreprise_id'] = entreprise.id
            messages.success(request, f'Entreprise {entreprise.nom} créée avec succès')
            return redirect('/dashboard/')
    else:
        form = EntrepriseForm()
    
    return render(request, 'parametres/creer_entreprise.html', {'form': form})

@login_required
def changer_entreprise(request, entreprise_id):
    """Changer d'entreprise"""
    entreprise = get_object_or_404(Entreprise, id=entreprise_id)
    
    if not entreprise.has_access(request.user):
        messages.error(request, 'Vous n\'avez pas accès à cette entreprise')
        return redirect('parametres:selection_entreprise')
    
    request.session['entreprise_id'] = entreprise.id
    messages.success(request, f'Entreprise changée pour : {entreprise.nom}')
    return redirect('/dashboard/')  # ✅ URL directe

# ============================================
# GESTION DES ENTREPRISES (Super Admin seulement)
# ============================================

@staff_member_required
def entreprise_liste(request):
    """Liste des entreprises - Super Admin seulement"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'super_admin':
        messages.error(request, 'Accès réservé au Super Administrateur.')
        return redirect('/dashboard/')
    
    entreprises = Entreprise.objects.all()
    return render(request, 'parametres/entreprise_list.html', {'entreprises': entreprises})


@staff_member_required
def entreprise_modifier(request, pk):
    """Modifier une entreprise - Super Admin seulement"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'super_admin':
        messages.error(request, 'Accès réservé au Super Administrateur.')
        return redirect('/dashboard/')
    
    entreprise = get_object_or_404(Entreprise, pk=pk)
    
    if request.method == 'POST':
        form = EntrepriseForm(request.POST, instance=entreprise)
        if form.is_valid():
            form.save()
            messages.success(request, f'Entreprise {entreprise.nom} modifiée avec succès')
            return redirect('parametres:entreprise_liste')
    else:
        form = EntrepriseForm(instance=entreprise)
    
    return render(request, 'parametres/entreprise_form.html', {'form': form, 'entreprise': entreprise})




# ============================================
# GESTION DES UTILISATEURS (admin uniquement)
# ============================================

@staff_member_required
def utilisateur_liste(request):
    """Liste des utilisateurs"""
    utilisateurs = User.objects.all()
    return render(request, 'parametres/utilisateurs/liste.html', {'utilisateurs': utilisateurs})


@staff_member_required
def utilisateur_creer(request):
    """Créer un utilisateur"""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'Utilisateur {user.username} créé avec succès')
            return redirect('parametres:utilisateur_liste')
    else:
        form = UserForm()
    
    return render(request, 'parametres/utilisateurs/form.html', {
        'form': form,
        'title': 'Créer un utilisateur',
        'button_text': 'Créer'
    })


@staff_member_required
def utilisateur_modifier(request, pk):
    """Modifier un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'Utilisateur {user.username} modifié avec succès')
            return redirect('parametres:utilisateur_liste')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'parametres/utilisateurs/form.html', {
        'form': form,
        'title': 'Modifier l\'utilisateur',
        'button_text': 'Enregistrer'
    })


@staff_member_required
def utilisateur_supprimer(request, pk):
    """Supprimer un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Utilisateur {username} supprimé avec succès')
        return redirect('parametres:utilisateur_liste')
    
    return render(request, 'parametres/utilisateurs/supprimer.html', {'user': user})


# ============================================
# GESTION DES PROFILS UTILISATEURS
# ============================================

# parametres/views.py - Version complète avec indentation correcte



@staff_member_required
def profil_liste(request):
    """Liste des profils utilisateurs - Super Admin seulement"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'super_admin':
        messages.error(request, 'Accès réservé au Super Administrateur.')
        return redirect('/dashboard/')
    
    profils = UserProfile.objects.all().select_related('user', 'entreprise')
    return render(request, 'parametres/profils/liste.html', {'profils': profils})


@staff_member_required
def profil_creer(request):
    """Créer un profil utilisateur - Super Admin seulement"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'super_admin':
        messages.error(request, 'Accès réservé au Super Administrateur.')
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.is_active = form.cleaned_data.get('is_active', True)
            user.is_staff = form.cleaned_data.get('is_staff', False)
            user.save()
            
            # Créer le profil
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Ajouter l'utilisateur à l'entreprise
            if profile.entreprise:
                profile.entreprise.utilisateurs.add(user)
            
            messages.success(request, f'Utilisateur {user.username} créé avec succès')
            return redirect('parametres:profil_liste')
    else:
        form = UserProfileForm()
    
    return render(request, 'parametres/profils/form.html', {
        'form': form,
        'title': 'Créer un utilisateur',
        'button_text': 'Créer'
    })


@staff_member_required
def profil_modifier(request, pk):
    """Modifier un profil utilisateur - Super Admin seulement"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'super_admin':
        messages.error(request, 'Accès réservé au Super Administrateur.')
        return redirect('/dashboard/')
    
    profile = get_object_or_404(UserProfile, pk=pk)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Mettre à jour l'utilisateur
            user = profile.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.is_active = form.cleaned_data.get('is_active', True)
            user.is_staff = form.cleaned_data.get('is_staff', False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            
            form.save()
            messages.success(request, f'Utilisateur {user.username} modifié avec succès')
            return redirect('parametres:profil_liste')
    else:
        form = UserProfileForm(instance=profile, initial={
            'username': profile.user.username,
            'email': profile.user.email,
            'is_active': profile.user.is_active,
            'is_staff': profile.user.is_staff,
        })
    
    return render(request, 'parametres/profils/form.html', {
        'form': form,
        'title': 'Modifier l\'utilisateur',
        'button_text': 'Enregistrer'
    })


@staff_member_required
def profil_supprimer(request, pk):
    """Supprimer un profil utilisateur - Super Admin seulement"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'super_admin':
        messages.error(request, 'Accès réservé au Super Administrateur.')
        return redirect('/dashboard/')
    
    profile = get_object_or_404(UserProfile, pk=pk)
    username = profile.user.username
    
    if request.method == 'POST':
        profile.user.delete()
        messages.success(request, f'Utilisateur {username} supprimé avec succès')
        return redirect('parametres:profil_liste')
    
    return render(request, 'parametres/profils/supprimer.html', {'profile': profile})