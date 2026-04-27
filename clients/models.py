# clients/models.py
from django.db import models
from parametres.models import Entreprise

class Client(models.Model):
    nom = models.CharField(max_length=200)
    personne_ressource = models.CharField(max_length=200, blank=True, null=True,verbose_name="Personne ressource")
    email = models.EmailField(blank=True, null=True)  # ✅ optionnel
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True, null=True)  # ✅ 
    
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

    @property
    def total_facture(self):
        """Total des factures payées de ce client"""
        total = sum(f.total_ttc for f in self.factures.filter(statut='payee'))
        return f"{total:,.2f}".replace(',', ' ')
    
    @property
    def nombre_factures(self):
        """Nombre de factures de ce client"""
        return self.factures.count()