# parametres/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class Entreprise(models.Model):
    """Modèle pour gérer plusieurs entreprises"""
    
    nom = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Identifiant unique")
    
    # Propriétaire
    proprietaire = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='entreprises_propriete'
    )
    
    # Utilisateurs ayant accès
    utilisateurs = models.ManyToManyField(
        User, 
        related_name='entreprises_acces',
        blank=True
    )
    
    # Actif
    est_active = models.BooleanField(default=True)
    
    # Date création
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
    
    def __str__(self):
        return self.nom
    
    def has_access(self, user):
        """Vérifie si l'utilisateur a accès"""
        return user == self.proprietaire or user in self.utilisateurs.all()
    
    @classmethod
    def get_user_entreprises(cls, user):
        """Récupère les entreprises de l'utilisateur"""
        return cls.objects.filter(
            Q(proprietaire=user) | Q(utilisateurs=user)
        ).distinct()


class ParametresEntreprise(models.Model):
    """Paramètres de l'entreprise (version multi-entreprise)"""
    
    # ✅ Lier à une entreprise
    entreprise = models.OneToOneField(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='parametres',
        null=True,
        blank=True
    )
    
    # Garder l'ancien système pour compatibilité
    id_unique = models.BooleanField(default=True, editable=False, null=True, blank=True)
    
    # Informations générales
    nom_entreprise = models.CharField(max_length=200, default="Mon Entreprise")
    slogan = models.CharField(max_length=200, blank=True)
    
    # Images
    logo = models.ImageField(upload_to='entreprises/logos/', blank=True, null=True)
    image_1 = models.ImageField(upload_to='entreprises/images/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='entreprises/images/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='entreprises/images/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='entreprises/images/', blank=True, null=True)
    
    # Coordonnées
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    #ajout telephone
    adresse = models.TextField()
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100, default="France")
    
    # Informations légales
    siret = models.CharField(max_length=14, blank=True)
    tva_intra = models.CharField(max_length=20, blank=True)
    capital_social = models.CharField(max_length=50, blank=True)
    forme_juridique = models.CharField(max_length=100, blank=True)
    rcs = models.CharField(max_length=50, blank=True)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # Banque
    iban = models.CharField(max_length=34, blank=True)
    #numero_compte = models.CharField(max_length=34, blank=True)
    bic = models.CharField(max_length=11, blank=True)
    #code_banque = models.CharField(max_length=34, blank=True)
    #cle_rib = models.CharField(max_length=5, blank=True)
    banque = models.CharField(max_length=100, blank=True)
    
    # Mentions légales
    mentions_legales = models.TextField(blank=True)
    conditions_paiement = models.TextField(blank=True, default="Paiement à réception de facture")
    pied_page_facture = models.TextField(blank=True)
    
    # Dates
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètres de l'entreprise"
        verbose_name_plural = "Paramètres de l'entreprise"
        unique_together = [['entreprise', 'id_unique']] if 'entreprise' in vars() else []
    
    def __str__(self):
        if self.entreprise:
            return f"Paramètres - {self.entreprise.nom}"
        return f"Paramètres - {self.nom_entreprise}"
    
    @classmethod
    def get_instance(cls, entreprise=None):
        """Récupère les paramètres pour une entreprise donnée"""
        if entreprise:
            instance, created = cls.objects.get_or_create(entreprise=entreprise)
            return instance
        # Fallback pour l'ancien système
        instance, created = cls.objects.get_or_create(id_unique=True, entreprise__isnull=True)
        return instance


class ParametresFacturation(models.Model):
    """Paramètres de facturation (version multi-entreprise)"""
    
    # ✅ Lier à une entreprise
    entreprise = models.OneToOneField(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='parametres_facturation',
        null=True,
        blank=True
    )
    
    # Garder l'ancien système
    id_unique = models.BooleanField(default=True, editable=False, null=True, blank=True)
    
    # Numérotation
    prefixe_facture = models.CharField(max_length=10, default="F")
    annee_dans_numero = models.BooleanField(default=True)
    separateur = models.CharField(max_length=5, default="-")
    prochain_numero = models.IntegerField(default=1)
    
    # Échéances
    delai_paiement_jours = models.IntegerField(default=30)
    
    # TVA par défaut
    tva_par_defaut = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    
    # Options
    envoyer_email_auto = models.BooleanField(default=False)
    rappel_paiement_auto = models.BooleanField(default=False)
    jours_avant_relance = models.IntegerField(default=7)
    
    # Devise
    devise = models.CharField(max_length=3, default="EUR", 
                              choices=[('EUR', 'Euro €'), ('USD', 'Dollar $'), ('GBP', 'Livre £'), ('XOF', 'Franc CFA')])
    
    class Meta:
        verbose_name = "Paramètres de facturation"
        verbose_name_plural = "Paramètres de facturation"
    
    def __str__(self):
        if self.entreprise:
            return f"Paramètres facturation - {self.entreprise.nom}"
        return "Paramètres de facturation"
    
    @classmethod
    def get_instance(cls, entreprise=None):
        """Récupère les paramètres pour une entreprise donnée"""
        if entreprise:
            instance, created = cls.objects.get_or_create(entreprise=entreprise)
            return instance
        # Fallback pour l'ancien système
        instance, created = cls.objects.get_or_create(id_unique=True, entreprise__isnull=True)
        return instance