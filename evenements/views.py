# evenements/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from decimal import Decimal
from .models import Evenement
from .forms import EvenementForm
from config.mixins import NotLecteurMixin

# Vues pour Evenement
class EvenementListView(LoginRequiredMixin, ListView):
    model = Evenement
    template_name = 'evenements/liste.html'
    context_object_name = 'evenements'
    paginate_by = 10
    
    def get_queryset(self):
        return Evenement.objects.filter(entreprise=self.request.entreprise_courante).order_by('-date_debut')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from clients.models import Client
        context['clients'] = Client.objects.filter(entreprise=self.request.entreprise_courante)
        context['statut_choices'] = Evenement.STATUT_CHOICES
        return context


class EvenementDetailView(LoginRequiredMixin, DetailView):
    model = Evenement
    template_name = 'evenements/detail.html'
    context_object_name = 'evenement'
    
    def get_queryset(self):
        return Evenement.objects.filter(entreprise=self.request.entreprise_courante)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evenement = self.get_object()
        context['total_facture'] = sum(f.total_ttc for f in evenement.factures.all())
        context['nombre_factures'] = evenement.factures.count()
        return context


class EvenementCreateView(LoginRequiredMixin, NotLecteurMixin, CreateView):
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
        self.object.entreprise = self.request.entreprise_courante
        self.object.save()
        messages.success(self.request, f'Événement "{self.object.nom}" créé avec succès !')
        return super().form_valid(form)


class EvenementUpdateView(LoginRequiredMixin, NotLecteurMixin, UpdateView):
    model = Evenement
    form_class = EvenementForm
    template_name = 'evenements/form.html'
    success_url = reverse_lazy('evenements:liste')
    
    def get_queryset(self):
        return Evenement.objects.filter(entreprise=self.request.entreprise_courante)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'événement'
        context['button_text'] = 'Enregistrer'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Événement "{form.instance.nom}" modifié avec succès !')
        return super().form_valid(form)


class EvenementDeleteView(LoginRequiredMixin, NotLecteurMixin, DeleteView):
    model = Evenement
    template_name = 'evenements/confirm_delete.html'
    success_url = reverse_lazy('evenements:liste')
    
    def get_queryset(self):
        return Evenement.objects.filter(entreprise=self.request.entreprise_courante)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nom_evenement = self.object.nom
        messages.success(request, f'L\'événement "{nom_evenement}" a été supprimé avec succès !')
        return super().delete(request, *args, **kwargs)