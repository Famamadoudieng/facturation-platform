# factures/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Facture, LigneFacture
from .forms import FactureForm, LigneFactureForm, LigneFactureFormSet
from clients.models import Client
from produits.models import Produit
from parametres.models import ParametresFacturation
from datetime import datetime
from decimal import Decimal
from django.urls import reverse, reverse_lazy 
from .exports import FactureExport, StatistiqueExport
from django.contrib.auth.mixins import UserPassesTestMixin
from config.mixins import NotLecteurMixin




class FactureListView(LoginRequiredMixin, ListView):
    model = Facture
    template_name = 'factures/list.html'
    context_object_name = 'factures'
    paginate_by = 10
    
    def get_queryset(self):
        # ✅ Filtrer par entreprise courante
        queryset = Facture.objects.filter(entreprise=self.request.entreprise_courante)
        
        # Filtres
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        type_facture = self.request.GET.get('type_facture')
        if type_facture:
            queryset = queryset.filter(type_facture=type_facture)
        
        date_debut = self.request.GET.get('date_debut')
        if date_debut:
            queryset = queryset.filter(date_facture__gte=date_debut)
        
        date_fin = self.request.GET.get('date_fin')
        if date_fin:
            queryset = queryset.filter(date_facture__lte=date_fin)
        
        client_id = self.request.GET.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        show_archived = self.request.GET.get('archives')
        if show_archived != 'oui':
            queryset = queryset.filter(est_archive=False)
        
        return queryset.order_by('-date_facture')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ✅ Filtrer les clients par entreprise courante
        context['clients'] = Client.objects.filter(entreprise=self.request.entreprise_courante).order_by('nom')
        context['total_ttc'] = sum(f.total_ttc for f in self.get_queryset())
        return context


class FactureDetailView(LoginRequiredMixin, DetailView):
    model = Facture
    template_name = 'factures/detail.html'
    context_object_name = 'facture'
    
    def get_queryset(self):
        # ✅ Sécuriser : ne voir que les factures de son entreprise
        return Facture.objects.filter(entreprise=self.request.entreprise_courante)


class FactureCreateView(LoginRequiredMixin, NotLecteurMixin, CreateView):
    model = Facture
    form_class = FactureForm
    template_name = 'factures/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # ✅ Passer la requête
        return kwargs    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer une facture'
        context['button_text'] = 'Créer la facture'
        return context
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        # ✅ Ajouter l'entreprise courante
        self.object.entreprise = self.request.entreprise_courante
        self.object.type_facture = 'proforma'
        self.object.statut = 'proforma'
        
        if not self.object.numero:
            self.object.numero = self.object.generer_numero()
            
        self.object.save()
        # Sauvegarder les relations many-to-many
        form.save_m2m()
        
        taux_display = dict(Facture.TAUX_TVA_CHOICES).get(self.object.taux_tva, self.object.taux_tva)
        messages.success(
            self.request, 
            f'✅ Facture {self.object.numero} créée avec succès ! TVA: {taux_display}'
        )
        
        return redirect('factures:detail', pk=self.object.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, '❌ Erreur dans le formulaire.')
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erreur dans {field}: {error}")
        return super().form_invalid(form)


class FactureUpdateView(LoginRequiredMixin, NotLecteurMixin, UpdateView):
    model = Facture
    form_class = FactureForm
    template_name = 'factures/form_with_lines.html'
    
    def get_queryset(self):
        # ✅ Sécuriser : ne modifier que les factures de son entreprise
        return Facture.objects.filter(entreprise=self.request.entreprise_courante)
    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        print(f"=== DEBUG get_context_data ===")
        print(f"Facture dans context: {self.object.pk if hasattr(self, 'object') else 'Pas de facture'}")
        print(f"Date facture: {self.object.date_facture if hasattr(self, 'object') else 'None'}")
        
        context['title'] = f'Modifier la facture {self.object.numero}'
        context['button_text'] = 'Enregistrer les modifications'

        # ✅ Forcer les valeurs initiales dans le formulaire
        if not self.request.POST:
            # Initialiser le formulaire avec les valeurs de la facture
            form = self.get_form()
            form.initial = {
                'client': self.object.client.id,
                'date_facture': self.object.date_facture,
                'date_echeance': self.object.date_echeance,
                'taux_tva': self.object.taux_tva,
                'notes': self.object.notes,
                'conditions': self.object.conditions,
            }
            context['form'] = form
        
        if self.request.POST:
            context['formset'] = LigneFactureFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = LigneFactureFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, f'Facture {self.object.numero} modifiée avec succès !')
            return redirect('factures:detail', pk=self.object.pk)
        else:
            for error in formset.errors:
                if error:
                    messages.error(self.request, f'Erreur dans les lignes: {error}')
            return self.render_to_response(self.get_context_data(form=form))
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur dans le formulaire principal.')
        return super().form_invalid(form)


class FactureDeleteView(LoginRequiredMixin, NotLecteurMixin, DeleteView):
    model = Facture
    template_name = 'factures/confirm_delete.html'
    success_url = reverse_lazy('factures:list')
    
    def get_queryset(self):
        # ✅ Sécuriser : ne supprimer que les factures de son entreprise
        return Facture.objects.filter(entreprise=self.request.entreprise_courante)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer la facture'
        return context
    
    def delete(self, request, *args, **kwargs):
        facture = self.get_object()
        numero = facture.numero
        
        if facture.statut == 'payee':
            messages.error(request, f'Impossible de supprimer une facture déjà payée: {numero}')
            return redirect('factures:detail', pk=facture.pk)
        
        messages.success(request, f'Facture {numero} supprimée avec succès!')
        return super().delete(request, *args, **kwargs)


@login_required
def ajouter_produit(request, pk):
        # ✅ Vérifier que l'utilisateur n'est pas lecteur
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'ajouter un produit.')
        return redirect('factures:detail', pk=pk)
    # ✅ Sécuriser avec l'entreprise
    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    
    if facture.type_facture != 'proforma':
        messages.error(request, 'Seules les factures proforma peuvent être modifiées.')
        return redirect('factures:detail', pk=pk)
    
    if request.method == 'POST':
        produit_id = request.POST.get('produit')
        quantite = request.POST.get('quantite', 1)
        prix = request.POST.get('prix', 0)
        designation = request.POST.get('designation', '')
        
        if not designation:
            messages.error(request, 'La désignation est obligatoire.')
            return redirect('factures:ajouter_produit', pk=pk)
        
        try:
            quantite = int(quantite)
            prix = Decimal(str(prix))
        except (ValueError, TypeError):
            messages.error(request, 'Valeurs numériques invalides.')
            return redirect('factures:ajouter_produit', pk=pk)
        
        produit = None
        if produit_id and produit_id != '':
            try:
                produit = Produit.objects.get(pk=produit_id)
                #designation = produit.nom
            except Produit.DoesNotExist:
                pass
        
        LigneFacture.objects.create(
            facture=facture,
            produit=produit,
            designation=designation,
            quantite=quantite,
            prix_unitaire_ht=prix
        )
        
        messages.success(request, f'Produit "{designation}" ajouté à la facture!')
        return redirect('factures:detail', pk=facture.pk)
    
    produits = Produit.objects.filter(entreprise=request.entreprise_courante).order_by('nom')
    return render(request, 'factures/ajouter_produit.html', {
        'facture': facture,
        'produits': produits
    })


def supprimer_ligne(request, pk):
    # ✅ Vérifier que l'utilisateur n'est pas lecteur
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission de supprimer une ligne.')
        return redirect('factures:detail', pk=pk)

    ligne = get_object_or_404(LigneFacture, pk=pk)
    facture_pk = ligne.facture.pk
    ligne.delete()
    messages.success(request, 'Produit supprimé de la facture!')
    return redirect('factures:detail', pk=facture_pk)


@login_required
def finaliser_facture(request, pk):

    # ✅ Vérifier que l'utilisateur n'est pas lecteur
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission de finaliser une facture.')
        return redirect('factures:detail', pk=pk)

    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    
    if facture.type_facture == 'definitive':
        messages.warning(request, 'Cette facture est déjà définitive.')
        return redirect('factures:detail', pk=pk)
    
    if facture.lignes.count() == 0:
        messages.error(request, 'Impossible de finaliser une facture sans ligne.')
        return redirect('factures:update', pk=pk)
    
    facture.type_facture = 'definitive'
    facture.statut = 'definitive'
    facture.save()
    
    messages.success(request, f'✅ Facture {facture.numero} devenue définitive !')
    return redirect('factures:detail', pk=facture.pk)


@login_required
def annuler_facture(request, pk):
    # ✅ Bloquer les lecteurs
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'annuler une facture.')
        return redirect('factures:detail', pk=pk)

    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    
    if facture.statut == 'payee':
        messages.error(request, 'Impossible d\'annuler une facture déjà payée.')
        return redirect('factures:detail', pk=pk)
    
    if facture.statut == 'annulee':
        messages.warning(request, 'Cette facture est déjà annulée.')
        return redirect('factures:detail', pk=pk)
    
    facture.statut = 'annulee'
    facture.save()
    
    messages.success(request, f'La facture {facture.numero} a été annulée.')
    return redirect('factures:detail', pk=pk)


@login_required
def marquer_envoyee(request, pk):
    # ✅ Bloquer les lecteurs
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'annuler une facture.')
        return redirect('factures:detail', pk=pk)

    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    
    if facture.statut == 'annulee':
        messages.error(request, 'Impossible de marquer une facture annulée comme envoyée.')
        return redirect('factures:detail', pk=pk)
    
    if facture.statut == 'payee':
        messages.warning(request, 'Cette facture est déjà payée.')
        return redirect('factures:detail', pk=pk)
    
    if facture.statut == 'proforma':
        messages.warning(request, 'Une facture proforma doit d\'abord être finalisée.')
        return redirect('factures:detail', pk=pk)
    
    facture.statut = 'envoyee'
    facture.save()
    
    messages.success(request, f'La facture {facture.numero} a été marquée comme envoyée.')
    return redirect('factures:detail', pk=pk)


@login_required
def marquer_payee(request, pk):
# ✅ Bloquer les lecteurs
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'annuler une facture.')
        return redirect('factures:detail', pk=pk)

    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    
    if facture.statut == 'annulee':
        messages.error(request, 'Impossible de marquer une facture annulée comme payée.')
        return redirect('factures:detail', pk=pk)
    
    if facture.statut == 'proforma':
        messages.warning(request, 'Une facture proforma ne peut pas être marquée comme payée.')
        return redirect('factures:detail', pk=pk)
    
    facture.statut = 'payee'
    facture.save()
    
    messages.success(request, f'La facture {facture.numero} a été marquée comme payée.')
    return redirect('factures:detail', pk=pk)


@login_required
def marquer_impayee(request, pk):
# ✅ Bloquer les lecteurs
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'annuler une facture.')
        return redirect('factures:detail', pk=pk)

    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    
    if facture.statut == 'payee':
        messages.error(request, 'Cette facture est déjà payée.')
        return redirect('factures:detail', pk=pk)
    
    if facture.statut == 'annulee':
        messages.error(request, 'Cette facture est annulée.')
        return redirect('factures:detail', pk=pk)
    
    facture.statut = 'impayee'
    facture.save()
    
    messages.warning(request, f'La facture {facture.numero} a été marquée comme impayée.')
    return redirect('factures:detail', pk=pk)


@login_required
def archiver_facture(request, pk):

    # ✅ Bloquer les lecteurs
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'annuler une facture.')
        return redirect('factures:detail', pk=pk)

    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    
    if facture.statut not in ['definitive', 'annulee', 'payee', 'impayee']:
        messages.warning(request, 'Seules les factures finalisées peuvent être archivées.')
        return redirect('factures:detail', pk=pk)
    
    facture.est_archive = True
    facture.save()
    
    messages.success(request, f'La facture {facture.numero} a été archivée.')
    return redirect('factures:detail', pk=pk)


@login_required
def desarchiver_facture(request, pk):

    # ✅ Bloquer les lecteurs
    if hasattr(request.user, 'profile') and request.user.profile.role == 'lecteur':
        messages.error(request, 'Vous n\'avez pas la permission d\'annuler une facture.')
        return redirect('factures:detail', pk=pk)
    facture = get_object_or_404(Facture, pk=pk, entreprise=request.entreprise_courante)
    facture.est_archive = False
    facture.save()
    messages.success(request, f'La facture {facture.numero} a été désarchivée.')
    return redirect('factures:detail', pk=pk)


@login_required
def exporter_factures_csv(request):
    """Exporte les factures en CSV"""
    factures = Facture.objects.filter(entreprise=request.entreprise_courante)
    
    statut = request.GET.get('statut')
    if statut:
        factures = factures.filter(statut=statut)
    
    date_debut = request.GET.get('date_debut')
    if date_debut:
        factures = factures.filter(date_facture__gte=date_debut)
    
    date_fin = request.GET.get('date_fin')
    if date_fin:
        factures = factures.filter(date_facture__lte=date_fin)
    
    return FactureExport.exporter_csv(factures, request)


@login_required
def exporter_factures_excel(request):
    """Exporte les factures en Excel"""
    factures = Facture.objects.filter(entreprise=request.entreprise_courante)
    
    statut = request.GET.get('statut')
    if statut:
        factures = factures.filter(statut=statut)
    
    return FactureExport.exporter_excel(factures, request)


@login_required
def exporter_statistiques_excel(request):
    """Exporte les statistiques des factures"""
    factures = Facture.objects.filter(entreprise=request.entreprise_courante)
    return StatistiqueExport.exporter_statistiques_excel(factures, request)