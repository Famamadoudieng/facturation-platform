# evenements/models.py
from django.db import models
from django.utils import timezone
from parametres.models import Entreprise
from clients.models import Client

class Evenement(models.Model):
    # Types d'événements prédéfinis
    TYPE_CHOICES = [
        ('Mariage', 'Mariage'),
        ('Séminaire', 'Séminaire'),
        ('Conférence', 'Conférence'),
        ('Anniversaire', 'Anniversaire'),
        ('Gala', 'Gala'),
        ('Team Building', 'Team Building'),
        ('Dîner', 'Dîner'),
        ('Lunch', 'Lunch'),
        ('Cocktail', 'Cocktail'),
        ('Réunion', 'Réunion'),
        ('Formation', 'Formation'),
        ('Hebergement', 'Hébergement'),
        ('Autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]
    
    nom = models.CharField(
        max_length=200, 
        choices=TYPE_CHOICES,  # ✅ Liste déroulante
        default='Autre',
        verbose_name="Nom de l'événement"
    )
    
    
    # ✅ Supprimer type_event (plus besoin)
    
    # Dates
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin", blank=True, null=True)
    date_arrivee = models.DateField(verbose_name="Date d'arrivée", blank=True, null=True)
    date_depart = models.DateField(verbose_name="Date de départ", blank=True, null=True)
    heure_debut = models.TimeField(verbose_name="Heure de début", blank=True, null=True)
    heure_fin = models.TimeField(verbose_name="Heure de fin", blank=True, null=True)
    
    # Lieu
    lieu = models.CharField(max_length=300, verbose_name="Lieu", blank=True)
       
    # Participants
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='evenements', verbose_name="Client")
    nombre_personnes = models.IntegerField(default=0, verbose_name="Nombre de personnes")
    
 
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie', verbose_name="Statut")
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Entreprise
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='evenements',
        null=True,
        blank=True
    )
    @property
    def nb_nuits(self):
        """Calcule le nombre de nuits (si les deux dates sont renseignées)"""
        if self.date_arrivee and self.date_depart:
            return (self.date_depart - self.date_arrivee).days
        return 0
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
    
    def __str__(self):
        return f"{self.nom} - {self.client.nom}"
    
