# paiements/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from factures.models import Facture
from .models import Paiement
from .forms import PaiementForm
from .exports import PaiementExport, StatistiquePaiementExport


@login_required
def ajouter_paiement(request, facture_pk):
    """Ajouter un paiement à une facture"""
    #verifie si le user est un lecteur
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'ajouter un paiement.')
        return redirect('factures:detail', pk=facture_pk)


    # ✅ Sécuriser avec l'entreprise
    facture = get_object_or_404(Facture, pk=facture_pk, entreprise=request.entreprise_courante)
    
    if facture.statut == 'payee':
        messages.warning(request, 'Cette facture est déjà entièrement payée.')
        return redirect('factures:detail', pk=facture_pk)
    
    if request.method == 'POST':
        form = PaiementForm(request.POST, facture=facture)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.facture = facture
            paiement.entreprise = request.entreprise_courante  # ✅ Ajouter l'entreprise
            paiement.statut = 'confirme'
            paiement.save()
            
            messages.success(
                request, 
                f'✅ Paiement de {paiement.montant:,.2f} FCFA enregistré avec succès!'
            )
            return redirect('factures:detail', pk=facture_pk)
    else:
        form = PaiementForm(facture=facture)
    
    context = {
        'facture': facture,
        'form': form,
        'title': 'Enregistrer un paiement',
        'reste_a_payer': facture.total_ttc - facture.total_paye,
    }
    return render(request, 'paiements/form.html', context)


@login_required
def annuler_paiement(request, pk):
    """Annuler un paiement"""
    # ✅ Sécuriser avec l'entreprise
    paiement = get_object_or_404(Paiement, pk=pk, entreprise=request.entreprise_courante)
    facture = paiement.facture
    
    if paiement.statut == 'annule':
        messages.warning(request, 'Ce paiement est déjà annulé.')
        return redirect('factures:detail', pk=facture.pk)
    
    paiement.statut = 'annule'
    paiement.save()
    
    messages.success(request, f'Paiement {paiement.numero_paiement} annulé avec succès.')
    return redirect('factures:detail', pk=facture.pk)


@login_required
def liste_paiements(request):
    """Liste de tous les paiements de l'entreprise"""
    # ✅ Filtrer par entreprise courante
    paiements = Paiement.objects.filter(entreprise=request.entreprise_courante).order_by('-date_paiement')
    
    # Filtres optionnels
    statut = request.GET.get('statut')
    if statut:
        paiements = paiements.filter(statut=statut)
    
    mode = request.GET.get('mode')
    if mode:
        paiements = paiements.filter(mode_paiement=mode)
    
    context = {
        'paiements': paiements,
        'total_paiements': paiements.count(),
        'total_montant': sum(p.montant for p in paiements if p.statut == 'confirme'),
        'statut_choices': Paiement.STATUT_CHOICES,
        'mode_choices': Paiement.MODE_PAIEMENT_CHOICES,
    }
    return render(request, 'paiements/liste.html', context)


@login_required
def detail_paiement(request, pk):
    """Détail d'un paiement"""
    # ✅ Sécuriser avec l'entreprise
    paiement = get_object_or_404(Paiement, pk=pk, entreprise=request.entreprise_courante)
    return render(request, 'paiements/detail.html', {'paiement': paiement})


@login_required
def modifier_paiement(request, pk):
    """Modifier un paiement existant"""
    # ✅ Sécuriser avec l'entreprise
    paiement = get_object_or_404(Paiement, pk=pk, entreprise=request.entreprise_courante)
    facture = paiement.facture
    
    if paiement.statut == 'annule':
        messages.error(request, 'Impossible de modifier un paiement annulé.')
        return redirect('factures:detail', pk=facture.pk)
    
    if request.method == 'POST':
        form = PaiementForm(request.POST, instance=paiement, facture=facture)
        if form.is_valid():
            paiement = form.save()
            paiement.mettre_a_jour_statut_facture()
            
            type_paiement = "Acompte" if facture.type_facture == 'proforma' else "Paiement"
            messages.success(request, f'✅ {type_paiement} modifié avec succès!')
            return redirect('factures:detail', pk=facture.pk)
    else:
        form = PaiementForm(instance=paiement, facture=facture)
    
    context = {
        'paiement': paiement,
        'facture': facture,
        'form': form,
        'title': f'Modifier {"l\'acompte" if facture.type_facture == "proforma" else "le paiement"}',
        'est_acompte': facture.type_facture == 'proforma',
        'reste_a_payer': facture.total_ttc - facture.total_paye + paiement.montant,
    }
    return render(request, 'paiements/form_modifier.html', context)


# ============================================
# EXPORTS
# ============================================

@login_required
def exporter_paiements_csv(request):
    """Exporte les paiements en CSV"""
    # ✅ Filtrer par entreprise courante
    paiements = Paiement.objects.filter(entreprise=request.entreprise_courante)
    
    statut = request.GET.get('statut')
    if statut:
        paiements = paiements.filter(statut=statut)
    
    mode = request.GET.get('mode')
    if mode:
        paiements = paiements.filter(mode_paiement=mode)
    
    date_debut = request.GET.get('date_debut')
    if date_debut:
        paiements = paiements.filter(date_paiement__gte=date_debut)
    
    date_fin = request.GET.get('date_fin')
    if date_fin:
        paiements = paiements.filter(date_paiement__lte=date_fin)
    
    return PaiementExport.exporter_csv(paiements, request)


@login_required
def exporter_paiements_excel(request):
    """Exporte les paiements en Excel"""
    # ✅ Filtrer par entreprise courante
    paiements = Paiement.objects.filter(entreprise=request.entreprise_courante)
    
    statut = request.GET.get('statut')
    if statut:
        paiements = paiements.filter(statut=statut)
    
    return PaiementExport.exporter_excel(paiements, request)


@login_required
def exporter_statistiques_paiements(request):
    """Exporte les statistiques des paiements"""
    # ✅ Filtrer par entreprise courante
    paiements = Paiement.objects.filter(entreprise=request.entreprise_courante)
    return StatistiquePaiementExport.exporter_statistiques_excel(paiements, request)