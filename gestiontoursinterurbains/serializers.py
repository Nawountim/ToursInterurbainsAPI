from rest_framework import serializers
from .models import Utilisateur, Vehicule,Administrateur, Trajet, Tour, Reservation, Chauffeur, Voyageur, Proprietaire, Wallet_transaction, Momo_transaction

class utilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['nom','prenom','date_naissance','sexe', 'contact', 'email', 'password']
        
class voyageurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voyageur
        fields = ['nom_complet','contact','user_id']
        
class proprietaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proprietaire
        fields = ['user_id']        
        
class administrateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrateur
        fields = ['nom','contact', 'email', 'password']     
        
class chauffeurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chauffeur
        fields = ['numero_permis','Categorie_permis','user_id']         
           
class vehiculeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicule
        fields = ['marque','plaque','nb_place', 'proprietaire_id']
        
class trajetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trajet
        fields = ['libelle','distance','start_longitude', 'start_latitude','end_longitude','end_latitude']

class tourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['libelle','chauffeur_id','vehicule_id', 'date','heure','trajet_id' ,'prix', 'capacite']
            
class reservationSerializer(serializers.ModelSerializer):
    class Meta:
            model = Reservation         
            fields = ['nb_place','tour_id','latitude_pickup','prix','longitude_pickup']
        
                               
class momoTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Momo_transaction
        fields = ['id_requete','statuscode','message','numero_transaction', 'montant', 'reference_operateur_id', 'operateur']                                       
        
        
class walletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet_transaction
        fields = ['montant','solde_initial','solde_restant','service', 'user_id', 'reservation_id']        