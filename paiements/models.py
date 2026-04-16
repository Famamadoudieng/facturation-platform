# paiements/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from factures.models import Facture
from parametres.models import Entreprise

class Paiement(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement bancaire'),
        ('carte', 'Carte bancaire'),
        ('mobile', 'Mobile money'),
        ('autres', 'Autres'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
    ]
    
    # Références
    facture = models.ForeignKey(Facture, on_delete=models.PROTECT, related_name='paiements')
    numero_paiement = models.CharField(max_length=50, unique=True, verbose_name="Numéro de paiement")
    
    # Informations paiement
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, verbose_name="Mode de paiement")
    montant = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant payé"
    )
    date_paiement = models.DateField(verbose_name="Date de paiement")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence (chèque, transaction)")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='paiements',
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-date_paiement']
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
    
    def __str__(self):
        return f"{self.numero_paiement} - {self.facture.numero} - {self.montant} FCFA"
    
    def save(self, *args, **kwargs):
        if not self.numero_paiement:
            self.numero_paiement = self.generer_numero()
        super().save(*args, **kwargs)
        
        # Mettre à jour le statut de la facture après chaque paiement
        self.mettre_a_jour_statut_facture()
    
    def generer_numero(self):
        """Génère un numéro de paiement unique"""
        from datetime import datetime
        annee = datetime.now().strftime('%Y')
        mois = datetime.now().strftime('%m')
        
        compteur = Paiement.objects.filter(
            created_at__year=datetime.now().year,
            created_at__month=datetime.now().month
        ).count() + 1
        
        return f"PAY-{annee}{mois}-{compteur:04d}"
    
    def mettre_a_jour_statut_facture(self):
        """Met à jour le statut de la facture en fonction des paiements"""
        from django.db.models import Sum
        
        total_paye = self.facture.paiements.filter(statut='confirme').aggregate(
            total=Sum('montant')
        )['total'] or Decimal('0.00')
        
        if total_paye >= self.facture.total_ttc:
            self.facture.statut = 'payee'
        elif total_paye > 0:
            self.facture.statut = 'partiel'
        else:
            if self.facture.statut not in ['definitive', 'envoyee']:
                self.facture.statut = 'definitive'
        
        self.facture.save(update_fields=['statut'])