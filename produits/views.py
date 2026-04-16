# produits/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Produit
from .forms import ProduitForm
from config.mixins import NotLecteurMixin

class ProduitListView(LoginRequiredMixin, ListView):
    model = Produit
    template_name = 'produits/list.html'
    context_object_name = 'produits'
    paginate_by = 10
    
    def get_queryset(self):
        # ✅ Filtrer par entreprise courante
        return Produit.objects.filter(entreprise=self.request.entreprise_courante)


class ProduitDetailView(LoginRequiredMixin, DetailView):
    model = Produit
    template_name = 'produits/detail.html'
    context_object_name = 'produit'
    
    def get_queryset(self):
        # ✅ Sécuriser : ne voir que les produits de son entreprise
        return Produit.objects.filter(entreprise=self.request.entreprise_courante)


class ProduitCreateView(LoginRequiredMixin, NotLecteurMixin, CreateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'produits/form.html'
    success_url = reverse_lazy('produits:list')
    
    def form_valid(self, form):
        # ✅ Ajouter l'entreprise courante
        self.object = form.save(commit=False)
        self.object.entreprise = self.request.entreprise_courante
        self.object.save()
        
        messages.success(self.request, 'Produit créé avec succès!')
        return redirect('produits:list')


class ProduitUpdateView(LoginRequiredMixin, NotLecteurMixin, UpdateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'produits/form.html'
    success_url = reverse_lazy('produits:list')
    
    def get_queryset(self):
        # ✅ Sécuriser : ne modifier que les produits de son entreprise
        return Produit.objects.filter(entreprise=self.request.entreprise_courante)
    
    def form_valid(self, form):
        messages.success(self.request, 'Produit modifié avec succès!')
        return super().form_valid(form)


class ProduitDeleteView(LoginRequiredMixin, NotLecteurMixin, DeleteView):
    model = Produit
    template_name = 'produits/confirm_delete.html'
    success_url = reverse_lazy('produits:list')
    
    def get_queryset(self):
        # ✅ Sécuriser : ne supprimer que les produits de son entreprise
        return Produit.objects.filter(entreprise=self.request.entreprise_courante)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Produit supprimé avec succès!')
        return super().delete(request, *args, **kwargs)