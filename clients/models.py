# clients/models.py
from django.db import models
from parametres.models import Entreprise

class Client(models.Model):
    nom = models.CharField(max_length=200)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField()
    
    # ✅ Ajouter ce champ (même si tu ne l'utilises pas)
    #code_postal = models.CharField(max_length=10, blank=True, null=True)
    
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='clients',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['nom']