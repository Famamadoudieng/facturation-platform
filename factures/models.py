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
        ('definitive', 'En réglement'),
        ('envoyee', 'Envoyée'),
        ('partiel', 'Partiellement soldé'),
        ('payee', 'Soldé'),
        ('annulee', 'Annulée'),
        ('impayee', 'Impayée'),
    ]
    
    # TVA Choices
    TAUX_TVA_CHOICES = [
        (10, '10%'),
        (18, '18%'),
        (0, '0% (Exonéré)'),
    ]
    
    # Informations générales
    numero = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='factures', verbose_name="Client")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_facture = models.DateField(verbose_name="Date de facture")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    # ✅ Ajouter ce champ pour la date de finalisation
    date_finalisation = models.DateTimeField( null=True, blank=True, verbose_name="Date de finalisation")
    # les dates pour hebeergement
    date_arrivee = models.DateField(null=True, blank=True, verbose_name="Date d'arrivée")
    date_depart = models.DateField(null=True, blank=True, verbose_name="Date de départ")
    # Type et Statut
    type_facture = models.CharField(max_length=20, choices=TYPE_CHOICES, default='proforma', verbose_name="Type de facture")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proforma', verbose_name="Statut")
    
    # taux tva
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, verbose_name="Taux TVA (%)")
    
    # Archive
    est_archive = models.BooleanField(default=False, verbose_name="Archivée")
    
    # Notes
    notes = models.TextField(blank=True, default="Prestation: Atelier du x mois année /x pax x jours")
    conditions = models.TextField(blank=True, default="Bon de commande à la confirmation de la commande, versement des 50% avant l'atelier et les 50% restant à la fin de l'atelier", verbose_name="Conditions de paiement")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='factures', null=True, blank=True)
    
    # Relation avec événement
    evenement = models.ForeignKey('evenements.Evenement', on_delete=models.CASCADE, null=True, blank=True, related_name='factures', verbose_name="Événement lié")
    
    # Champs pour les commissions
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant de la commission")
    taux_commission = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux de commission (%)")
    commissionnaire = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom du commissionnaire")
    
    class Meta:
        ordering = ['-date_facture']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
    
    def __str__(self):
        return f"{self.numero} - {self.client.nom} - {self.date_facture}"
    
    # ✅ AJOUTER LA MÉTHODE save() ICI (pas dans LigneFacture)
    def save(self, *args, **kwargs):
        """Sauvegarde avec génération automatique du numéro"""
        #print(f"🔍 save() - numero avant: '{self.numero}'")
        
        if not self.numero or self.numero == "":
            self.numero = self.generer_numero()
            print(f"🔍 Numéro généré: '{self.numero}'")
        
        super().save(*args, **kwargs)
        #print(f"✅ Sauvegardé: {self.numero}")
    
    # ✅ AJOUTER LA MÉTHODE generer_numero() ICI
    def generer_numero(self):
        """Génère un numéro de facture unique"""
        from datetime import datetime
        
        # Utiliser date_facture si disponible
        date_ref = self.date_facture if self.date_facture else datetime.now().date()
        annee = date_ref.strftime('%Y')
        mois = date_ref.strftime('%m')
        
        #print(f"🔍 generer_numero() - Date: {annee}-{mois}")
        
        # Compter les factures du mois
        compteur = Facture.objects.filter(
            date_facture__year=int(annee),
            date_facture__month=int(mois)
        ).count() + 1
        
        numero = f"FACT-{annee}{mois}-{compteur:04d}"
        
        # Sécurité anti-doublon
        while Facture.objects.filter(numero=numero).exists():
            compteur += 1
            numero = f"FACT-{annee}{mois}-{compteur:04d}"
        
        return numero
    
    # Propriétés
    @property
    def est_exonere(self):
        return self.taux_tva == 0
    
    @property
    def total_ht(self):
        total = Decimal('0.00')
        for ligne in self.lignes.all():
            total += ligne.total_ht
        return total
    
    @property
    def montant_tva(self):
        return self.total_ht * (self.taux_tva / Decimal('100'))
    
    @property
    def total_ttc(self):
        return self.total_ht + self.montant_tva
    
    @property
    def total_paye(self):
        from django.db.models import Sum
        total = self.paiements.filter(statut='confirme').aggregate(total=Sum('montant'))['total']
        return total or Decimal('0.00')
    
    @property
    def reste_a_payer(self):
        return self.total_ttc - self.total_paye
    
    @property
    def nom_evenement(self):
        return self.evenement.nom if self.evenement else None
    
    @property
    def montant_commission(self):
        if self.taux_commission > 0:
            return self.total_ttc * (self.taux_commission / Decimal('100'))
        return self.commission
    
    @property
    def net_a_payer(self):
        return self.total_ttc - self.montant_commission

    @property
    def nb_nuits(self):
        """Calcule le nombre de nuits (si les deux dates sont renseignées)"""
        if self.date_arrivee and self.date_depart:
            return (self.date_depart - self.date_arrivee).days
        return 0

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
        return self.quantite * self.prix_unitaire_ht
    
    @property
    def total_ttc(self):
        return self.total_ht
  