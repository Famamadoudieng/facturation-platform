# clients/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Client
from .forms import ClientForm
from config.mixins import NotLecteurMixin

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/list.html'
    context_object_name = 'clients'
    paginate_by = 10
    
    def get_queryset(self):
        # ✅ Filtrer par entreprise courante
        queryset = Client.objects.filter(entreprise=self.request.entreprise_courante)
        
        # Recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(telephone__icontains=search_query) |
                Q(adresse__icontains=search_query)
            )
        
        # Filtre par ordre alphabétique
        order_by = self.request.GET.get('order', 'nom')
        if order_by == 'nom':
            queryset = queryset.order_by('nom')
        elif order_by == '-nom':
            queryset = queryset.order_by('-nom')
        elif order_by == 'date':
            queryset = queryset.order_by('-id')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_order'] = self.request.GET.get('order', 'nom')
        # ✅ Compter uniquement les clients de l'entreprise courante
        context['total_clients'] = Client.objects.filter(entreprise=self.request.entreprise_courante).count()
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/detail.html'
    context_object_name = 'client'
    
    def get_queryset(self):
        # ✅ Sécuriser : ne voir que les clients de son entreprise
        return Client.objects.filter(entreprise=self.request.entreprise_courante)


class ClientCreateView(LoginRequiredMixin, NotLecteurMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('clients:list')
    
    def form_valid(self, form):
        # ✅ Ajouter l'entreprise courante
        self.object = form.save(commit=False)
        self.object.entreprise = self.request.entreprise_courante
        self.object.save()
        
        messages.success(self.request, f'Le client "{self.object.nom}" a été créé avec succès !')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un client'
        context['button_text'] = 'Créer le client'
        context['icon'] = 'user-plus'
        return context


class ClientUpdateView(LoginRequiredMixin, NotLecteurMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('clients:list')
    
    def get_queryset(self):
        # ✅ Sécuriser : ne modifier que les clients de son entreprise
        return Client.objects.filter(entreprise=self.request.entreprise_courante)
    
    def form_valid(self, form):
        messages.success(self.request, f'Le client "{form.instance.nom}" a été modifié avec succès !')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le client'
        context['button_text'] = 'Enregistrer les modifications'
        context['icon'] = 'user-edit'
        return context


class ClientDeleteView(LoginRequiredMixin,  NotLecteurMixin, DeleteView):
    model = Client
    template_name = 'clients/confirm_delete.html'
    success_url = reverse_lazy('clients:list')
    
    def get_queryset(self):
        # ✅ Sécuriser : ne supprimer que les clients de son entreprise
        return Client.objects.filter(entreprise=self.request.entreprise_courante)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nom_client = self.object.nom
        messages.success(self.request, f'Le client "{nom_client}" a été supprimé avec succès !')
        return super().delete(request, *args, **kwargs)