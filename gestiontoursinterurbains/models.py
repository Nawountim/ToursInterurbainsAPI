from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

current_date = timezone.now().date()
# Create your models here.

#Classe Utilisateur
class Utilisateur(models.Model):
    SEX_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    ]
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=20, null= False)
    prenom = models.CharField(max_length=30, null= False)
    date_naissance = models.DateTimeField(null= False)
    sexe = models.CharField(max_length=1, choices=SEX_CHOICES) 
    contact = models.CharField(max_length=10, null= False)
    email = models.EmailField(unique=True, null= False)
    password = models.CharField(max_length= 60, null= False)
    portefeuille = models.FloatField(default=0)
    is_voyageur = models.BooleanField(default=False)
    is_fournisseur = models.BooleanField(default=False)
    is_chauffeur = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    class Meta:
        db_table = "utilisateur"
        

#Classe Voyageur
class Voyageur(models.Model):
    
    id = models.AutoField(primary_key=True)
    nom_complet = models.CharField( max_length = 50 )
    contact = models.CharField(max_length = 10)
    user_id = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True)
      
    class Meta:
        db_table = "voyageur"
        
#Classe Proprietaire
class Proprietaire(models.Model):
    
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
      
    class Meta:
        db_table = "proprietaire"   
        
        
#Classe Chauffeur

class Chauffeur(models.Model):
    
    id = models.AutoField(primary_key= True)
    user_id = models.ForeignKey(Utilisateur,null= False, on_delete=models.CASCADE)
    numero_permis = models.CharField(max_length = 30, null= False, blank=False)
    Categorie_permis = models.CharField(max_length = 1, null= False)
    statut = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.numero_permis}"
    
    class Meta:
        db_table = "chauffeur"
        
        
                          
        
class Administrateur(models.Model):
    
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length = 30,null= False)
    contact = models.CharField(max_length = 10, default=0)
    email = models.CharField(max_length = 60,null= False)
    password = models.CharField(max_length = 60,null= False)
       
    class Meta:
        db_table = "administrateur"                
        

#Classe Vehicule

class Vehicule(models.Model):
   
    id = models.AutoField(primary_key=True)
    marque = models.CharField(max_length = 25, null= False, blank=False)
    visite_technique = models.BooleanField(default=True)
    plaque = models.CharField(max_length = 15, null= False)
    statut = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    nb_place = models.IntegerField()
    proprietaire_id = models.ForeignKey(Proprietaire,null= False, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.marque}"
    
    class Meta:
        db_table = "vehicule"
        
        

#Classe Trajet
   
class Trajet(models.Model):
    # Champs du trajet
    id = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=50)
    distance = models.FloatField()
    start_longitude = models.FloatField()
    start_latitude = models.FloatField()
    end_longitude = models.FloatField()
    end_latitude = models.FloatField()

    def __str__(self):
        return f"{self.libelle}"

    class Meta:
        db_table = "trajet"
         
         
#Classe Tour
      
class Tour(models.Model):
    # Champs du tour
    id = models.AutoField(primary_key= True)
    id_tour = models.CharField(max_length=10, unique=True)
    libelle  = models.CharField(max_length=50)
    prix = models.FloatField()
    statut = models.BooleanField(default=True)
    chauffeur_id = models.ForeignKey(Chauffeur, on_delete=models.SET_NULL, null=True, blank=True)
    vehicule_id = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True)
    nb_reservation = models.IntegerField(default=0)
    date = models.DateTimeField()
    heure = models.TimeField()
    trajet_id = models.ForeignKey(Trajet, on_delete = models.CASCADE )
    capacite = models.IntegerField()
    


    
    def __str__(self):
        return f"{self.libelle}"
    
    class Meta:
        db_table = "tour" 
             
             
#Classe Reservation
             
class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    id_reservation = models.CharField(max_length=10, unique=True)
    voyageur_id = models.ForeignKey(Voyageur, on_delete=models.CASCADE)
    nb_place = models.IntegerField()
    tour_id = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reservations')
    latitude_pickup = models.FloatField()
    longitude_pickup = models.FloatField()
    prix = models.FloatField()
    statut_paiement = models.BooleanField(default=False)
    canal_paiement = models.CharField(max_length=20, default="")
    transaction_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    transaction_id = models.TextField(null=True)
    transaction = GenericForeignKey('transaction_type', 'transaction_id')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réservation #{self.id_reservation} - {self.voyageur_id.nom_complet}"

    class Meta:
        db_table = "reservation"

        
#Classe Momo_transaction

class Momo_transaction(models.Model):
    id = models.AutoField(primary_key=True)     
    id_requete = models.TextField(max_length = 75)
    statuscode = models.CharField(max_length = 25, null= False)
    message =  models.CharField(max_length = 30)
    numero_transaction = models.BigIntegerField()
    montant = models.FloatField()
    reference_operateur_id = models.BigIntegerField()
    operateur = models.CharField(max_length = 30)
    type = models.CharField(max_length = 30)
    user_id = models.IntegerField(default=None)
    date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.message}"
    
    class Meta:
        db_table = "momo_transaction" 
        
        
#Classe Wallet_transaction

class Wallet_transaction(models.Model):
    id = models.AutoField(primary_key=True)
    montant = models.FloatField()
    solde_initial = models.FloatField()
    solde_restant = models.FloatField()
    service = models.TextField()
    user_id = models.ForeignKey(Utilisateur, on_delete=models.DO_NOTHING, null=False)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.DO_NOTHING, null= False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service}"

    class Meta:
        db_table = "wallet_transaction"
