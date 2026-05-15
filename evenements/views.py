# evenements/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Evenement
from .forms import EvenementForm
from parametres.models import Entreprise  # ← utilisation du modèle Entreprise (multi-entreprise)

class NotLecteurMixin:
    """Placeholder pour les permissions si besoin"""
    pass

class EvenementListView(LoginRequiredMixin, ListView):
    model = Evenement
    template_name = 'evenements/liste.html'
    context_object_name = 'evenements'
    paginate_by = 10

    def get_queryset(self):
        # Récupérer l'entreprise depuis la session
        entreprise_id = self.request.session.get('entreprise_id')
        if not entreprise_id:
            return Evenement.objects.none()

        queryset = Evenement.objects.filter(entreprise_id=entreprise_id)

        # Filtre par statut
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        # Filtre par client
        client_id = self.request.GET.get('client')
        if client_id and client_id.isdigit():
            queryset = queryset.filter(client_id=int(client_id))

        return queryset.order_by('-date_debut')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from clients.models import Client
        context['clients'] = Client.objects.all()
        context['statut_choices'] = Evenement.STATUT_CHOICES
        return context

class EvenementDetailView(LoginRequiredMixin, DetailView):
    model = Evenement
    template_name = 'evenements/detail.html'
    context_object_name = 'evenement'

    def get_queryset(self):
        entreprise_id = self.request.session.get('entreprise_id')
        if entreprise_id:
            return Evenement.objects.filter(entreprise_id=entreprise_id)
        return Evenement.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Optionnel : ajouter des statistiques sur les factures liées
        # evenement = self.get_object()
        # context['total_facture'] = sum(f.total_ttc for f in evenement.factures.all())
        return context

class EvenementCreateView(LoginRequiredMixin, CreateView):
    model = Evenement
    form_class = EvenementForm
    template_name = 'evenements/form.html'
    success_url = reverse_lazy('evenements:liste')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer un événement'
        context['button_text'] = 'Créer'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # Récupérer l'entreprise courante depuis la session
        entreprise_id = self.request.session.get('entreprise_id')
        if entreprise_id:
            try:
                self.object.entreprise = Entreprise.objects.get(id=entreprise_id)
            except Entreprise.DoesNotExist:
                messages.error(self.request, "Entreprise non trouvée.")
                return redirect('evenements:liste')
        else:
            # Fallback : prendre la première entreprise existante
            self.object.entreprise = Entreprise.objects.first()
        self.object.save()
        messages.success(self.request, f'Événement "{self.object.nom}" créé avec succès !')
        return super().form_valid(form)

class EvenementUpdateView(LoginRequiredMixin, UpdateView):
    model = Evenement
    form_class = EvenementForm
    template_name = 'evenements/form.html'
    success_url = reverse_lazy('evenements:liste')

    def get_queryset(self):
        entreprise_id = self.request.session.get('entreprise_id')
        if entreprise_id:
            return Evenement.objects.filter(entreprise_id=entreprise_id)
        return Evenement.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'événement'
        context['button_text'] = 'Enregistrer'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Événement "{form.instance.nom}" modifié avec succès !')
        return super().form_valid(form)

class EvenementDeleteView(LoginRequiredMixin, DeleteView):
    model = Evenement
    template_name = 'evenements/confirm_delete.html'
    success_url = reverse_lazy('evenements:liste')

    def get_queryset(self):
        entreprise_id = self.request.session.get('entreprise_id')
        if entreprise_id:
            return Evenement.objects.filter(entreprise_id=entreprise_id)
        return Evenement.objects.none()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nom_evenement = self.object.nom
        messages.success(request, f'L\'événement "{nom_evenement}" a été supprimé avec succès !')
        return super().delete(request, *args, **kwargs)