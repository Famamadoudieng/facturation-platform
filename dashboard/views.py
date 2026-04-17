from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import datetime, timedelta
from decimal import Decimal
from factures.models import Facture, LigneFacture
from clients.models import Client
from produits.models import Produit
from paiements.models import Paiement


def connexion(request):
    """Page de connexion personnalisée"""
    if request.user.is_authenticated:
        return redirect('/')  # ✅ Redirige vers la racine
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username}!')
            return redirect('/')  # ✅ Redirige vers la racine
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')
            return render(request, 'dashboard/connexion.html')
    
    return render(request, 'dashboard/connexion.html')

@login_required
def home(request):
    """Page d'accueil après connexion"""
    return render(request, 'dashboard/home.html')

@login_required
def dashboard(request):
    now = datetime.now()
    
    # ✅ Récupérer l'entreprise courante
    entreprise = request.entreprise_courante
    
    if not entreprise:
        return render(request, 'dashboard/index.html', {
            'message': 'Veuillez sélectionner une entreprise',
            'entreprise_courante': None
        })
    
    # ✅ Filtrer toutes les requêtes par entreprise
    factures = Facture.objects.filter(entreprise=entreprise)
    clients = Client.objects.filter(entreprise=entreprise)
    paiements = Paiement.objects.filter(entreprise=entreprise)
    
    # === STATISTIQUES GÉNÉRALES ===
    
    # Chiffre d'affaires total (factures payées uniquement)
    ca_total = Decimal('0.00')
    for facture in factures.filter(statut='payee'):
        ca_total += facture.total_ttc
    
    # Chiffre d'affaires du mois
    ca_mois = Decimal('0.00')
    for facture in factures.filter(statut='payee', date_facture__year=now.year, date_facture__month=now.month):
        ca_mois += facture.total_ttc
    
    # Chiffre d'affaires de l'année
    ca_annee = Decimal('0.00')
    for facture in factures.filter(statut='payee', date_facture__year=now.year):
        ca_annee += facture.total_ttc
    
    # === STATISTIQUES FACTURES ===
    total_factures = factures.count()
    factures_payees = factures.filter(statut='payee').count()
    factures_impayees = factures.filter(statut='impayee').count()
    factures_en_attente = factures.filter(statut__in=['envoyee', 'proforma', 'definitive']).count()
    
    # Taux de paiement
    taux_paiement = (factures_payees / total_factures * 100) if total_factures > 0 else 0
    
    # === FACTURES PAR MOIS (12 derniers mois) ===
    factures_par_mois = []
    ca_par_mois = []
    
    for i in range(11, -1, -1):
        date = datetime(now.year, now.month, 1) - timedelta(days=30*i)
        mois = date.strftime('%b %Y')
        
        # Nombre de factures
        nb_factures = factures.filter(
            date_facture__year=date.year,
            date_facture__month=date.month
        ).count()
        
        # CA du mois
        ca_mois_data = Decimal('0.00')
        for facture in factures.filter(statut='payee', date_facture__year=date.year, date_facture__month=date.month):
            ca_mois_data += facture.total_ttc
        
        factures_par_mois.append({'mois': mois, 'nombre': nb_factures})
        ca_par_mois.append({'mois': mois, 'ca': float(ca_mois_data)})
    
    # === TOP CLIENTS ===
    top_clients = []
    for client in clients:
        total_ca = Decimal('0.00')
        nb_factures = 0
        for facture in client.factures.filter(statut='payee', entreprise=entreprise):
            total_ca += facture.total_ttc
            nb_factures += 1
        if nb_factures > 0:
            top_clients.append({
                'nom': client.nom,
                'factures': nb_factures,
                'ca': float(total_ca)
            })
    
    top_clients = sorted(top_clients, key=lambda x: x['ca'], reverse=True)[:5]
    
    # === TOP PRODUITS ===
    top_produits = []
    produits_vendus = {}
    
    for ligne in LigneFacture.objects.filter(facture__entreprise=entreprise):
        nom = ligne.designation
        if nom in produits_vendus:
            produits_vendus[nom] += ligne.quantite
        else:
            produits_vendus[nom] = ligne.quantite
    
    for nom, quantite in sorted(produits_vendus.items(), key=lambda x: x[1], reverse=True)[:5]:
        top_produits.append({'nom': nom, 'quantite': quantite})
    
    context = {
        'entreprise_courante': entreprise,
        'ca_total': float(ca_total),
        'ca_annee': float(ca_annee),
        'ca_mois': float(ca_mois),
        'total_factures': total_factures,
        'factures_payees': factures_payees,
        'factures_impayees': factures_impayees,
        'factures_en_attente': factures_en_attente,
        'taux_paiement': taux_paiement,
        'factures_par_mois': factures_par_mois,
        'ca_par_mois': ca_par_mois,
        'top_clients': top_clients,
        'top_produits': top_produits,
        'now': now,
    }
    
   
    return render(request, 'dashboard/index.html', context)