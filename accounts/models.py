# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from parametres.models import Entreprise

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Administrateur'),      # ✅ Gère toute la plateforme
        ('admin', 'Administrateur'),                  # ✅ Admin par entreprise
        ('comptable', 'Comptable'),
        ('commercial', 'Commercial'),
        ('lecteur', 'Lecteur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lecteur')
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='profils', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def has_perm(self, permission):
        """Vérifie les permissions selon le rôle"""
        # Super Admin : tout est permis
        if self.role == 'super_admin':
            return True
        
        permissions = {
            'admin': ['create', 'edit', 'delete', 'view', 'export', 'manage_team'],
            'comptable': ['create', 'edit', 'view', 'export'],
            'commercial': ['create', 'edit', 'view'],
            'lecteur': ['view', 'export'],
        }
        return permission in permissions.get(self.role, [])
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def is_admin_entreprise(self):
        return self.role == 'admin'
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"