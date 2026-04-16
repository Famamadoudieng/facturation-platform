# produits/models.py - Version ultra minimaliste
from django.db import models
from parametres.models import Entreprise

class Produit(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom du produit/service")
    description = models.TextField(blank=True, verbose_name="Description")
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='produits',
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['nom']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
    
    def __str__(self):
        return self.nom