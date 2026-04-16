# factures/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from clients.models import Client
from produits.models import Produit
from parametres.models import Entreprise

class Facture(models.Model):
    # Types de facture
    TYPE_CHOICES = [
        ('proforma', 'Proforma'),
        ('definitive', 'Définitive'),
    ]
    
    # Statuts de facture
    STATUT_CHOICES = [
        ('proforma', 'Proforma'),
        ('definitive', 'Définitive'),
        ('envoyee', 'Envoyée'),
        ('partiel', 'Partiellement payée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
        ('impayee', 'Impayée'),

    ]
    
    # TVA Choices - AJOUT DE L'OPTION EXONÉRÉ
    TAUX_TVA_CHOICES = [
        (0, '0% (Exonéré)'),
        (10, '10%'),
        (18, '18%'),
       
    ]
    
    # Informations générales
    numero = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='factures', verbose_name="Client")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_facture = models.DateField(verbose_name="Date de facture")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    
    # Type et Statut
    type_facture = models.CharField(max_length=20, choices=TYPE_CHOICES, default='proforma', verbose_name="Type de facture")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proforma', verbose_name="Statut")
    
# taux tva
    taux_tva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=18.00, 
        verbose_name="Taux TVA (%)"
    )



    # Archive
    est_archive = models.BooleanField(default=False, verbose_name="Archivée")
    
    # Notes
    notes = models.TextField(blank=True, default="Prestation: Atelier du x mois année /x pax x jours")
    conditions = models.TextField(blank=True, default="Bon de commande à la confirmation de la commande, versement des 50% avant l'atelier et les 50% restant à la fin de l'atelier", verbose_name="Conditions de paiement")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='factures',
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-date_facture']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
    
    def __str__(self):
        return f"{self.numero} - {self.client.nom} - {self.date_facture}"
    
    @property
    def est_exonere(self):
        """Vérifie si la facture est exonérée de TVA"""
        return self.taux_tva == 0
    
    @property
    def total_ht(self):
        """Calcul du total HT (somme des lignes)"""
        total = Decimal('0.00')
        for ligne in self.lignes.all():
            total += ligne.total_ht
        return total
    
    @property
    def montant_tva(self):
        """Calcul de la TVA sur le total HT"""
        return self.total_ht * (self.taux_tva / Decimal('100'))
    
    @property
    def total_ttc(self):
        """Calcul du total TTC = HT + TVA"""
        return self.total_ht + self.montant_tva
    
    def generer_numero(self):
        """Génère un numéro de facture unique"""
        from datetime import datetime
        annee = datetime.now().strftime('%Y')
        mois = datetime.now().strftime('%m')
        
        compteur = Facture.objects.filter(
            date_creation__year=datetime.now().year, 
            date_creation__month=datetime.now().month
        ).count() + 1
        
        return f"FACT-{annee}{mois}-{compteur:04d}"
        #@@@@@@@@@@@@@@@@paiment
    @property
    def total_paye(self):
        """Total des paiements confirmés"""
        from django.db.models import Sum
        total = self.paiements.filter(statut='confirme').aggregate(
            total=Sum('montant')
        )['total']
        return total or Decimal('0.00')
    
    @property
    def reste_a_payer(self):
        """Reste à payer"""
        return self.total_ttc - self.total_paye
    



class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes', verbose_name="Facture")
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='lignes_facture', verbose_name="Produit", null=True, blank=True)
    
    # Informations au moment de la facturation
    designation = models.CharField(max_length=200, verbose_name="Désignation")
    quantite = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Quantité", default=1)
    prix_unitaire_ht = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire HT", default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
    
    def __str__(self):
        return f"{self.facture.numero} - {self.designation}"
    
    @property
    def total_ht(self):
        """Total HT de la ligne"""
        return self.quantite * self.prix_unitaire_ht
    
    @property
    def total_ttc(self):
        """Total TTC de la ligne (identique au HT car TVA au niveau facture)"""
        return self.total_ht
    
    def save(self, *args, **kwargs):
        """Auto-remplir les champs si non fournis"""
        if not self.designation and self.produit:
            self.designation = self.produit.nom
        super().save(*args, **kwargs)




