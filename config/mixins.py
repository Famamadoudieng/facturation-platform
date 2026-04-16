# config/mixins.py
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin

class NotLecteurMixin(UserPassesTestMixin):
    """Mixin pour bloquer l'accès aux lecteurs (création, modification, suppression)"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role != 'lecteur'
        return True
    
    def handle_no_permission(self):
        messages.error(self.request, 'Vous n\'avez pas la permission d\'effectuer cette action.')
        return redirect('/dashboard/')


class SuperAdminRequiredMixin(UserPassesTestMixin):
    """✅ Seul le Super Admin peut accéder (gestion des entreprises, utilisateurs)"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role == 'super_admin'
        return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Accès réservé au Super Administrateur.')
        return redirect('/dashboard/')


class AdminRequiredMixin(UserPassesTestMixin):
    """✅ Super Admin ou Admin entreprise peuvent accéder"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if hasattr(self.request.user, 'profile'):
            role = self.request.user.profile.role
            return role in ['super_admin', 'admin']
        return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Accès réservé aux administrateurs.')
        return redirect('/dashboard/')


class ComptableRequiredMixin(UserPassesTestMixin):
    """✅ Comptable, Admin ou Super Admin peuvent accéder"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if hasattr(self.request.user, 'profile'):
            role = self.request.user.profile.role
            return role in ['super_admin', 'admin', 'comptable']
        return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Accès réservé aux comptables et administrateurs.')
        return redirect('/dashboard/')


class CommercialRequiredMixin(UserPassesTestMixin):
    """✅ Commercial, Comptable, Admin ou Super Admin peuvent accéder"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if hasattr(self.request.user, 'profile'):
            role = self.request.user.profile.role
            return role in ['super_admin', 'admin', 'comptable', 'commercial']
        return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'Vous n\'avez pas la permission nécessaire.')
        return redirect('/dashboard/')