from django.shortcuts import render
from django.http import JsonResponse
from .models import Utilisateur, Vehicule,Administrateur, Trajet, Tour, Reservation, Chauffeur, Voyageur, Proprietaire, Momo_transaction, Wallet_transaction
from .serializers import utilisateurSerializer,administrateurSerializer, proprietaireSerializer, vehiculeSerializer, trajetSerializer, voyageurSerializer, tourSerializer, momoTransactionSerializer, walletTransactionSerializer, reservationSerializer, chauffeurSerializer
import json
from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime
import calendar
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.utils import timezone
from django.views import View
from django.db.models import Sum
import bcrypt
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


# Create your views here.


                                    ### Fonction de la classe Administrateur  ###
@csrf_exempt
def create_user(data, serializer, model):
    if serializer.is_valid():
        # Hashage du mot de passe
        password = data['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Enregistrement de l'utilisateur avec le mot de passe hashé
        user = serializer.save(password=hashed_password.decode('utf-8'))
        return JsonResponse({"message": "success", "Info": f"{model} créé", "code": 200})
    else:
        return JsonResponse({"message": "error", "Info": f"{model} non créé", "code": 400})
    
@csrf_exempt
def create_administrateur(request):
    if request.method == "POST":
        data = json.loads(request.body)
        serializer = administrateurSerializer(data=data)
        return create_user(data, serializer, "Administrateur")
    return redirect("/get_admin")

@csrf_exempt
def create_utilisateur(request):
    if request.method == "POST":
        data = json.loads(request.body)
        serializer = utilisateurSerializer(data=data)
        return create_user(data, serializer, "Utilisateur")
    return redirect("/get_utilisateur")



        

            
#Liste des utilisateurs
def get_utilisateur(request):
    data = { "utilisateurs": [] }
    utilisateurs = Utilisateur.objects.all()
    for utilisateur in utilisateurs:
        data["utilisateurs"].append({
            "id": utilisateur.id,
            "nom": utilisateur.nom,
            "prenom": utilisateur.prenom,
            "date_naissance": utilisateur.date_naissance,
            "sexe": utilisateur.sexe,
            "contact": utilisateur.contact,
            "email": utilisateur.email,
            "portefeuille": utilisateur.portefeuille,
            "is_voyageur": utilisateur.is_voyageur,
            "is_fournisseur": utilisateur.is_fournisseur,
            "is_chauffeur": utilisateur.is_chauffeur,
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data)            

#Info d'un utilisateur
def get_one_utilisateur(request, id):
    data = { "utilisateur": [] }
    utilisateurs = Utilisateur.objects.filter(id=id)
    if utilisateurs:
        for utilisateur in utilisateurs:
            
            data["utilisateur"].append({
                "id": utilisateur.id,
                "nom": utilisateur.nom,
                "prenom": utilisateur.prenom,
                "date_naissance": utilisateur.date_naissance,
                "sexe": utilisateur.sexe,
                "contact": utilisateur.contact,
                "email": utilisateur.email,
                "portefeuille": utilisateur.portefeuille,
                "is_voyageur": utilisateur.is_voyageur,
                "is_fournisseur": utilisateur.is_fournisseur,
                "is_chauffeur": utilisateur.is_chauffeur,
                
                                    })
            """ Envoyer sous forme de Json: API """
        return JsonResponse(data) 
    
    return JsonResponse({"message": "Aucun utilisateur ne correspond"})
#Modification d'un utilisateur
@csrf_exempt
def update_utilisateur(request, id):
    utilisateur = get_object_or_404(Utilisateur, id=id)
    if request.method == 'POST':
        serializer = utilisateurSerializer(utilisateur, data=request.data)
        if serializer.is_valid():
            serializer.update(utilisateur, request.data)
            return JsonResponse({"info": "utilisateur modifié"})
        return JsonResponse({"error": serializer.errors})
            


#Suppression d'un utilisateur
@csrf_exempt
def delete_utilisateur(request, id):
    utilisateur = Utilisateur.objects.get(id=id)
    utilisateur.delete()
    
    
                                ###  Fonction de la classe Propriétaire  ###
@csrf_exempt                            
def create_proprietaire(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update_id = data['user_id']
        proprietaire_serializer = proprietaireSerializer(data=data)
        
        if proprietaire_serializer.is_valid():
            proprietaire_serializer.save()  # Sauvegarde du voyageur créé
            utilisateur = update_id  # Récupération de l'ID de l'utilisateur associé au voyageur
            utilisateur_obj = Utilisateur.objects.get(id=utilisateur)  # Récupération de l'objet utilisateur complet
            
            utilisateur_obj.is_fournisseur = True  # Mise à jour du champ is_voyageur à True
            utilisateur_obj.save()  # Sauvegarde de l'utilisateur modifié
            
            return JsonResponse({"Info": "Proprietaire créé"})
        else:
            return JsonResponse({"Info": "Proprietaire non créé"})
    return redirect("/get_proprietaire")

#Liste des Proprietaires
def get_proprietaire(request):
    data = {"proprietaires": []}
    proprietaires = Proprietaire.objects.all()
    
    for proprietaire in proprietaires:
        user_data = {
            "user_id": proprietaire.user_id.id,
            "nom": proprietaire.user_id.nom,
            "prenom": proprietaire.user_id.prenom
        }
        proprietaire_data = {
            "id": proprietaire.id,
            "user_data": user_data
        }
        data["proprietaires"].append(proprietaire_data)
    
    return JsonResponse(data)


#Suppression d'un Proprietaire
@csrf_exempt
def delete_proprietaire(request, id):
    proprietaire = Proprietaire.objects.get(id=id)
    proprietaire.delete()

                            ###  Fonction de la classe Voyageur  ###
                            
def create_voyageur(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update_id = data['user_id']
        voyageur_serializer = voyageurSerializer(data=data)
        
        if voyageur_serializer.is_valid():
            voyageur_serializer.save()  # Sauvegarde du voyageur créé
            utilisateur = update_id  # Récupération de l'ID de l'utilisateur associé au voyageur
            utilisateur_obj = Utilisateur.objects.get(id=utilisateur)  # Récupération de l'objet utilisateur complet
            
            utilisateur_obj.is_voyageur = True  # Mise à jour du champ is_voyageur à True
            utilisateur_obj.save()  # Sauvegarde de l'utilisateur modifié
            
            return JsonResponse({"Info": "Voyageur créé"})
        else:
            return JsonResponse({"Info": "Voyageur non créé"})
    return redirect("/get_voyageur")


#Suppression d'un Voyageur
@csrf_exempt
def delete_voyageur(request, id):
    voyageur = Voyageur.objects.get(id=id)
    voyageur.delete()
    
    
     
                            
                            ###  Fonction de la classe Chauffeur  ###                            
                            
                            
### Creer un chauffeur

@csrf_exempt
def create_chauffeur(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update_id = data['user_id']
        serializer = chauffeurSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            utilisateur = update_id  # Récupération de l'ID de l'utilisateur associé au voyageur
            utilisateur_obj = Utilisateur.objects.get(id=utilisateur)  # Récupération de l'objet utilisateur complet
            
            utilisateur_obj.is_chauffeur = True  # Mise à jour du champ is_voyageur à True
            utilisateur_obj.save()  # Sauvegarde de l'utilisateur modifié
            
            return JsonResponse({"Info": "chauffeur créé"})
        else:
         #return JsonResponse({"error": serializer.errors})
         return JsonResponse({"Info":"chauffeur non créé"})
    return redirect("/get_chauffeur")

        
            
#Liste des chauffeurs
def get_chauffeur(request):
    data = { "chauffeurs": [] }
    chauffeurs = Chauffeur.objects.all()
    for chauffeur in chauffeurs:
        data["chauffeurs"].append({
            "id": chauffeur.id,
            "nom": chauffeur.user_id.nom,
            "prenom": chauffeur.user_id.prenom,
            "numero_permis": chauffeur.numero_permis,
            "categorie": chauffeur.Categorie_permis,
            "statut": chauffeur.statut,
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data)            


#Liste des chauffeurs disponibles
def get_disponible_chauffeur(request):
    data = {"chauffeurs": []}
    chauffeurs = Chauffeur.objects.filter(statut=True)  # Filtrer les chauffeurs avec le statut "True" (ou "Disponible")

    for chauffeur in chauffeurs:
        data["chauffeurs"].append({
            "id": chauffeur.id,
            "nom": chauffeur.user_id.nom,
            "prenom": chauffeur.user_id.prenom,
            "numero_permis": chauffeur.numero_permis,
            "categorie": chauffeur.Categorie_permis,
            "statut": chauffeur.statut,
        })

    return JsonResponse(data)


#Avoir un chauffeur via son id
def get_one_chauffeur(request, id):
    data = {"chauffeurs": []}
    chauffeurs = Chauffeur.objects.filter(id=id)  # Filtrer les chauffeurs avec le statut "True" (ou "Disponible")

    for chauffeur in chauffeurs:
        data["chauffeurs"].append({
            "id": chauffeur.id,
            "nom": chauffeur.user_id.nom,
            "prenom": chauffeur.user_id.prenom,
            "numero_permis": chauffeur.numero_permis,
            "categorie": chauffeur.Categorie_permis,
            "statut": chauffeur.statut,
        })

    return JsonResponse(data)

#Avoir un chauffeur via son user_id
def get_one_chauffeur_by_user_id(request, user_id):
    data = {"chauffeurs": []}
    chauffeurs = Chauffeur.objects.filter(user_id=user_id)  # Filtrer les chauffeurs avec le statut "True" (ou "Disponible")

    for chauffeur in chauffeurs:
        data["chauffeurs"].append({
            "id": chauffeur.id,
            "numero_permis": chauffeur.numero_permis,
            "categorie": chauffeur.Categorie_permis,
            "statut": chauffeur.statut,
        })

    return JsonResponse(data)

#Liste des chauffeurs non-disponibles
def get_nondisponible_chauffeur(request):
    data = {"chauffeurs": []}
    chauffeurs = Chauffeur.objects.filter(statut=False)  # Filtrer les chauffeurs avec le statut "True" (ou "Disponible")

    for chauffeur in chauffeurs:
        data["chauffeurs"].append({
            "id": chauffeur.id,
            "nom": chauffeur.user_id.nom,
            "prenom": chauffeur.user_id.prenom,
            "numero_permis": chauffeur.numero_permis,
            "categorie": chauffeur.Categorie_permis,
            "statut": chauffeur.statut,
        })

    return JsonResponse(data)


#Modification d'un chauffeur
@csrf_exempt
def update_chauffeur(request, id):
    chauffeur = get_object_or_404(Chauffeur, id=id)
    if request.method == 'POST':
        serializer = chauffeurSerializer(chauffeur, data=request.data)
        if serializer.is_valid():
            serializer.update(chauffeur, request.data)
            return JsonResponse({"info": "chauffeur modifié"})
        return JsonResponse({"error": serializer.errors})
    
            
#Modification du statut d'un chauffeur
@csrf_exempt
def update_chauffeur_availability(request, id):
    c = get_object_or_404(Chauffeur, id=id)

    if request.method == 'POST':
        data = json.loads(request.body)
        statut_chauffeur = data['statut']
       
        if statut_chauffeur is None:
            return JsonResponse({"error": "Statut manquant"})

        if statut_chauffeur == 'true':
            c.statut = True
        elif statut_chauffeur == 'false':
            c.statut = False
        else:
            return JsonResponse({"error": "Statut invalide"})

        c.save()

        return JsonResponse({"info": "Statut de disponibilité modifié"})

    return JsonResponse({"error": "Statut de disponibilité non autorisé"})


#Suppression d'un chauffeur
@csrf_exempt
def delete_chauffeur(request, id):
    chauffeur = Chauffeur.objects.get(id=id)
    chauffeur.delete()                                                    
    
    
    
    
                                ### Fonction de la classe Trajet  ###
    
### Creer un trajet
@csrf_exempt
def create_trajet(request):
    if request.method == "POST":
        data = json.loads(request.body)
        serializer = trajetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"Info": "Trajet créé"})
        else:
         #return JsonResponse({"error": serializer.errors})
         return JsonResponse({"Info":"Trajet non créé"})
    return redirect("/get_trajet")   

 

            
#Liste des trajets
def get_trajet(request):
    data = { "trajets": [] }
    trajets = Trajet.objects.all()
    for trajet in trajets:
        data["trajets"].append({
            "id": trajet.id,
            "libelle": trajet.libelle,
            "distance": trajet.distance,
            "prix": trajet.prix,
            "longitude": trajet.longitude,
            "latitude": trajet.latitude,
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data)            


#Modification d'un trajet
@csrf_exempt
def update_trajet(request, id):
    trajet = get_object_or_404(Trajet, id=id)
    if request.method == 'POST':
        serializer = trajetSerializer(trajet, data=request.data)
        if serializer.is_valid():
            serializer.update(trajet, request.data)
            return JsonResponse({"info": "trajet modifié"})
        return JsonResponse({"error": serializer.errors})
            


#Suppression d'un trajet
@csrf_exempt
def delete_trajet(request, id):
    trajet = Trajet.objects.get(id=id)
    trajet.delete() 
    
    

                                ### Fonction de la classe Vehicule  ###

### Creer un Vehicule
@csrf_exempt
def create_vehicule(request):
    if request.method == "POST":
        data = json.loads(request.body)
        serializer = vehiculeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"Info": "Vehicule créé", "code": 200})
        else:
         #return JsonResponse({"error": serializer.errors})
         return JsonResponse({"Info":"Vehicule non créé", "code": 200})
    return redirect("/get_vehicule")   

 

            
#Liste des Vehicules
def get_vehicule(request):
    data = {"vehicules": []}
    vehicules = Vehicule.objects.all()
    
    data = {
            "vehicules": []
        }
    for vehicule in vehicules:
            data["vehicules"].append({
                "id": vehicule.id,
                "marque": vehicule.marque,
                "visite_technique": vehicule.visite_technique,
                "plaque": vehicule.plaque,
                "statut": vehicule.statut,
                "is_accepted": vehicule.is_accepted,
                "nb_place": vehicule.nb_place,
                "proprietaire_id": vehicule.proprietaire_id.id,
            })
    
    return JsonResponse(data)


#Vehicule disponible
def get_disponible_vehicule(request):
    data = {"vehicules": []}
    vehicules = Vehicule.objects.filter(statut=True)  # Filtrer les véhicules avec le statut "True" (ou "Disponible")

    for vehicule in vehicules:
        data["vehicules"].append({
            "id": vehicule.id,
            "marque": vehicule.marque,
            "visite_technique": vehicule.visite_technique,
            "plaque": vehicule.plaque,
            "statut": vehicule.statut,
            "latitude": vehicule.proprietaire_id,
        })

    return JsonResponse(data)


#Infos d'un vehicule           

def get_one_vehicule(request, id):
    data = {"vehicule": []}
    vehicules = Vehicule.objects.filter(id=id)
    
    if len(vehicules) == 0:
        return JsonResponse({"error": "Le véhicule spécifié n'existe pas."})
    
    for vehicule in vehicules:
        data["vehicule"].append({
            "id": vehicule.id,
            "marque": vehicule.marque,
            "visite_technique": vehicule.visite_technique,
            "plaque": vehicule.plaque,
            "statut": vehicule.statut,
            "is_accepted": vehicule.is_accepted,
            "nb_place": vehicule.nb_place,
            "proprietaire_id": vehicule.proprietaire_id.id,
        })
    
    return JsonResponse(data)

#Infos des vehicules par proprietaire

def get_vehicules_by_proprietaire(request, proprietaire_id):
    try:
        vehicules = Vehicule.objects.filter(proprietaire_id=proprietaire_id)
        data = {
            "vehicules": []
        }
        for vehicule in vehicules:
            data["vehicules"].append({
                "id": vehicule.id,
                "marque": vehicule.marque,
                "visite_technique": vehicule.visite_technique,
                "plaque": vehicule.plaque,
                "statut": vehicule.statut,
                "is_accepted": vehicule.is_accepted,
                "nb_place": vehicule.nb_place,
                "proprietaire_id": vehicule.proprietaire_id.id,
            })
        return JsonResponse(data)
    except Vehicule.DoesNotExist:
        return JsonResponse({"error": "Aucun véhicule trouvé pour le propriétaire spécifié."})
    
    
#Modification d'un Vehicule
@csrf_exempt
def update_vehicule(request, id):
    vehicule = get_object_or_404(Vehicule, id=id)
    if request.method == 'POST':
        serializer = vehiculeSerializer(vehicule, data=request.data)
        if serializer.is_valid():
            serializer.update(vehicule, request.data)
            return JsonResponse({"info": "vehicule modifié"})
        return JsonResponse({"error": serializer.errors})
            

#Modification du statut d'acceptation d'un vehicule
@csrf_exempt
def accept_vehicule(request, id):
    v = get_object_or_404(Vehicule, id=id)

    if request.method == 'POST':
        data = json.loads(request.body)
        statut_acccepted = data['is_accepted']
       
        if statut_acccepted is None:
            return JsonResponse({"error": "Statut manquant"})

        if statut_acccepted == 'true':
            v.is_accepted = True
        elif statut_acccepted == 'false':
            v.is_accepted = False
        else:
            return JsonResponse({"error": "Statut invalide"})

        v.save()

        return JsonResponse({"info": "Statut d'acceptation modifié"})

    return JsonResponse({"error": "Statut d'acceptation non autorisé"})

#Modification du statut de disponibilité d'un vehicule
@csrf_exempt
def update_vehicule_availability(request, id):
    v = get_object_or_404(Vehicule, id=id)

    if request.method == 'POST':
        data = json.loads(request.body)
        statut_vehicule = data['statut']
       
        if statut_vehicule is None:
            return JsonResponse({"error": "Statut manquant"})

        if statut_vehicule == 'true':
            v.statut = True
        elif statut_vehicule == 'false':
            v.statut = False
        else:
            return JsonResponse({"error": "Statut invalide"})

        v.save()

        return JsonResponse({"info": "Statut de disponibilité modifié","message":"success"})

    return JsonResponse({"error": "Statut de disponibilité non autorisé", "message":"error"})



#Suppression d'un Vehicule
@csrf_exempt
def delete_vehicule(request, id):
    vehicule = Vehicule.objects.get(id=id)
    vehicule.delete()    
    
    
     

                                ### Fonction de la classe Tour  ###

### Creer un Tour
@csrf_exempt
def create_tour(request):
    if request.method == "POST":
        data = json.loads(request.body)
        serializer = tourSerializer(data=data)
        if serializer.is_valid():
            tour = serializer.save()
            # Générer l'identifiant unique du tour 
            id_tour = None
            while not id_tour:
                last_id = Tour.objects.order_by('-id').first()
                if last_id:
                    last_id = last_id.id + 1
                else:
                    last_id = 1
                new_id_tour = f"TOUR{last_id:04d}"
                if Tour.objects.filter(id_tour=new_id_tour).exists():
                    # L'identifiant existe déjà, continuer la boucle pour en générer un nouveau
                    continue
                id_tour = new_id_tour
            
            # Assigner l'identifiant du tour au tour créée
            tour.id_tour = id_tour
            tour.save()
            return JsonResponse({"Info": "Tour créé"})
        else:
         #return JsonResponse({"error": serializer.errors})
         return JsonResponse({"Info":"Tour non créé"})
    return redirect("/get_tour")   

 

            
#Liste des Tours
def get_tour(request):
    data = { "tours": [] }
    tours = Tour.objects.all().order_by('date')

    for tour in tours:
        data["tours"].append({
            "id": tour.id,
           "libelle": tour.libelle,
            "id_tour": tour.id_tour,
            "statut": tour.statut,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "nb_reservation": tour.nb_reservation,
            "date": tour.date,
            "heure": tour.heure,
            "trajet_id": tour.trajet_id.id,
            "trajet": tour.trajet_id.libelle,
            "capacite": tour.capacite,
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data)            

#Avoir un tour
def get_one_tour(request, id):
    try:
        tour = Tour.objects.get(id=id)
        data = {
            "id": tour.id,
            "libelle": tour.libelle,
            "id_tour": tour.id_tour,
            "statut": tour.statut,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "nb_reservation": tour.nb_reservation,
            "date": tour.date,
            "heure": tour.heure,
            "trajet_id": tour.trajet_id.id,
             "trajet": tour.trajet_id.libelle,
            "capacite": tour.capacite,
        }
        return JsonResponse(data)
    except Tour.DoesNotExist:
        return JsonResponse({"message": "Tour non trouvé"})

#Avoir un tour
def get_tour_by_idtour(request, id_tour):
    try:
        tour = Tour.objects.get(id_tour=id_tour)
        data = {
            "id": tour.id,
            "libelle": tour.libelle,
            "id_tour": tour.id_tour,
            "statut": tour.statut,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "nb_reservation": tour.nb_reservation,
            "date": tour.date,
            "heure": tour.heure,
            "trajet_id": tour.trajet_id.id,
             "trajet": tour.trajet_id.libelle,
            "capacite": tour.capacite,
        }
        return JsonResponse(data)
    except Tour.DoesNotExist:
        return JsonResponse({"message": "Tour non trouvé"})

#Avoir tours pour un chauffeur
def get_tour_by_chauffeur(request, chauffeur_id):
    try:
        tours = Tour.objects.filter(chauffeur_id=chauffeur_id).order_by('-date')
        data = {"tours": []}
        for tour in tours:
            data["tours"].append({
                "id": tour.id,
               "libelle": tour.libelle,
                "id_tour": tour.id_tour,
                "libelle": tour.libelle,
                "statut": tour.statut,
                "chauffeur_id": tour.chauffeur_id.id,
                "chauffeur_nom": tour.chauffeur_id.user_id.nom,
                "vehicule_id": tour.vehicule_id.id,
                "nb_reservation": tour.nb_reservation,
                "date": tour.date,
                "heure": tour.heure,
                "trajet_id": tour.trajet_id.id,
                 "trajet": tour.trajet_id.libelle,
                "capacite": tour.capacite,
            })
        return JsonResponse(data)
    except Tour.DoesNotExist:
        return JsonResponse({"message": "Aucun tour trouvé pour ce chauffeur"})
    
#Avoir tours pour un vehicule
def get_tour_by_vehicule(request, vehicule_id):
    try:
        tours = Tour.objects.filter(vehicule_id=vehicule_id).order_by('-date')
        data = {"tours": []}
        for tour in tours:
            data["tours"].append({
                "id": tour.id,
                "libelle": tour.libelle,
                "id_tour": tour.id_tour,
                "libelle": tour.libelle,
                "statut": tour.statut,
                "chauffeur_id": tour.chauffeur_id.id,
                "chauffeur_nom": tour.chauffeur_id.user_id.nom,
                "vehicule_id": tour.vehicule_id.id,
                "nb_reservation": tour.nb_reservation,
                "date": tour.date,
                "heure": tour.heure,
                "trajet_id": tour.trajet_id.id,
                 "trajet": tour.trajet_id.libelle,
                "capacite": tour.capacite,
            })
        return JsonResponse(data)
    except Tour.DoesNotExist:
        return JsonResponse({"message": "Aucun tour trouvé pour ce véhicule"})
  
    
    
#Modification d'un Tour
@csrf_exempt
def update_tour(request, id):
    tour = get_object_or_404(Tour, id=id)
    if request.method == 'POST':
        serializer = tourSerializer(tour, data=request.data)
        if serializer.is_valid():
            serializer.update(tour, request.data)
            return JsonResponse({"info": "tour modifié"})
        return JsonResponse({"message": serializer.errors})
            


#Suppression d'un Tour
@csrf_exempt
def delete_tour(request, id):
    tour = Tour.objects.get(id=id)
    tour.delete()      
    
    
    
                                ### Fonction de la classe Wallet_transaction  ###

### Creer un Wallet_transaction
@csrf_exempt
@transaction.atomic
def create_wallet_transaction(request):
    if request.method == "POST":
        data = json.loads(request.body)
        reservation_id = data['reservation_id']

        try:
            with transaction.atomic():
                serializer = walletTransactionSerializer(data=data)
                if serializer.is_valid():
                    wallet_transaction = serializer.save()

                    try:
                        reservation = Reservation.objects.get(id=reservation_id)
                    except Reservation.DoesNotExist:
                        print('Reservation inexistant')
                        return JsonResponse({"error": "La réservation spécifiée n'existe pas.", "code": 404})

                    # Mettre à jour les champs de la réservation
                    reservation.canal_paiement = "Wallet Transaction"
                    reservation.statut_paiement = True
                    reservation.transaction_id = wallet_transaction.id
                    reservation.transaction_type = ContentType.objects.get_for_model(Wallet_transaction)
                    print('Reservation mise a jour')
                    # Sauvegarder les modifications de la réservation
                    reservation.save()

                    try:
                        user_id = data['user_id']
                        utilisateur = Utilisateur.objects.get(id=user_id)
                    except Utilisateur.DoesNotExist:
                        print('utilisateur inexistant')
                        return JsonResponse({"error": "L'utilisateur spécifié n'existe pas.", 'code': 404})

                    # Mettre à jour le portefeuille du client
                    solde_restant = data['solde_restant']
                    utilisateur.portefeuille = solde_restant
                    utilisateur.save()
                    print('Wallet TR Creer')
                    return JsonResponse({"Info": "Wallet transaction créée avec succès et réservation mise à jour.", 'code': 200})
                else:
                    print('Serializer non valide')
                    return JsonResponse({"Info": "Échec de la création de la wallet transaction.", 'code': 400})
        except Exception as e:
            print(f'Une erreur s\'est produite lors de la création de la transaction de portefeuille : {str(e)}')
            return JsonResponse({"Info": "Une erreur s'est produite lors de la création de la wallet transaction.", 'code': 500})

    return redirect("/get_wallet_transaction")


 

            
#Liste des Wallet_transaction
def get_wallet_transaction(request):
    data = { "wallet_transactions": [] }
    wallet_transactions = Wallet_transaction.objects.all()
    for wallet_transaction in wallet_transactions:
        nom_payant = wallet_transaction.user_id.nom
        prenom_payant = wallet_transaction.user_id.prenom
        data["wallet_transactions"].append({
            "id": wallet_transaction.id,
            "date": wallet_transaction.date,
            "montant": wallet_transaction.montant,
            "solde_initial": wallet_transaction.solde_initial,
            "solde_restant": wallet_transaction.solde_restant,
            "service": wallet_transaction.service,
            "user_id": wallet_transaction.user_id.id,
            "reservation_id": wallet_transaction.reservation_id.id,
            "nom_payant": f"{nom_payant} {prenom_payant}"
        })
    
    return JsonResponse(data)
            

#Liste des wallet_transactions pour un utilisateur et en ordre recent
def get_wallet_transactions_by_user(request, user_id):
    transactions = Wallet_transaction.objects.filter(user_id=user_id).order_by('-date')
    
    data = {
        "wallet_transactions": []
    }
    
    for transaction in transactions:
        data["wallet_transactions"].append({
            "id": transaction.id,
            "montant": transaction.montant,
            "solde_initial": transaction.solde_initial,
            "solde_restant": transaction.solde_restant,
            "service": transaction.service,
            "user_id": transaction.user_id.id,
            "date": transaction.date,
            "nom du payant": transaction.user_id.nom 
        })
    
    return JsonResponse(data)

#Avoir un wallet transaction
def get_wallet_transaction_by_id(request, transaction_id):
    try:
        transaction = Wallet_transaction.objects.get(id=transaction_id)
        data = {
            "id": transaction.id,
            "montant": transaction.montant,
            "solde_initial": transaction.solde_initial,
            "solde_restant": transaction.solde_restant,
            "service": transaction.service,
            "user_id": transaction.user_id.id,
            "reservation_id": transaction.reservation_id.id,
            "date": transaction.date,
            "nom du payant": transaction.user_id.nom
        }
        return JsonResponse(data)
    except Wallet_transaction.DoesNotExist:
        return JsonResponse({"error": "La transaction de portefeuille spécifiée n'existe pas."}, status=404)


#Modification d'un Wallet_transaction
@csrf_exempt
def update_wallet_transaction(request, id):
    wallet_transaction = get_object_or_404(Wallet_transaction, id=id)
    if request.method == 'POST':
        serializer = Wallet_transaction(wallet_transaction, data=request.data)
        if serializer.is_valid():
            serializer.update(wallet_transaction, request.data)
            return JsonResponse({"info": "wallet transaction modifié"})
        return JsonResponse({"error": serializer.errors})
            


#Suppression d'un Wallet_transaction
@csrf_exempt
def delete_wallet_transaction(request, id):
    wallet_transaction = Wallet_transaction.objects.get(id=id)
    wallet_transaction.delete()          
    
    
    
                                ### Fonction de la classe Momo_transaction  ###

### Creer un Momo_transaction
@csrf_exempt
def create_momo_transaction(request, id_reservation):
    data = json.loads(request.body)
    # Extraire les informations de la réponse en fonction de l'opérateur
    if "code" in data:  # TMONEY
        # Extraire les données de la transaction Momo
        id_requete = data["idRequete"]
        statuscode = data["code"]
        message = data["statutRequete"]
        numero_transaction = data["numeroClient"]
        montant = float(data["montant"])
        reference_operateur_id = data["refTmoney"]
        operateur = data["operateur"]
        transaction_type = data["typeRequete"]
        user_id = data["user_id"]
        

        # Vérifier si l'ID de réservation correspond à une réservation existante
        try:
            reservation = Reservation.objects.get(id_reservation=id_reservation)
        except Reservation.DoesNotExist:
            reservation = None

        if reservation:
            # Créer la transaction Momo et l'associer à la réservation
            momo_transaction = Momo_transaction.objects.create(
                id_requete=id_requete,
                statuscode=statuscode,
                message=message,
                numero_transaction=numero_transaction,
                montant=montant,
                reference_operateur_id=reference_operateur_id,
                operateur=operateur,
                type=transaction_type,
                user_id = user_id,
               
            )

            # Mettre à jour le champ canal_paiement dans la réservation
            reservation.statut_paiement = True
            reservation.canal_paiement = "Momo Transaction"
            reservation.transaction_type = ContentType.objects.get_for_model(Momo_transaction)
            reservation.transaction_id = momo_transaction.id_requete
            reservation.save()

            # Renvoyer une réponse JSON avec le statut de création
            return JsonResponse({"success": True, "message": "Momo transaction créée avec succès"})
        try:
            utilisateur = Utilisateur.objects.get(id=int(id_reservation))
        except Utilisateur.DoesNotExist:
            utilisateur = None

        if utilisateur:
            # Mettre à jour le portefeuille de l'utilisateur avec le montant de la transaction
            utilisateur.portefeuille += montant
            utilisateur.save()
            # Créer la transaction Momo sans association à une réservation
            momo_transaction = Momo_transaction.objects.create(
                id_requete=id_requete,
                statuscode=statuscode,
                message=message,
                numero_transaction=numero_transaction,
                montant=montant,
                reference_operateur_id=reference_operateur_id,
                operateur=operateur,
                type=transaction_type,
                user_id=user_id,
            )

            # Renvoyer une réponse JSON avec le statut de création
            return JsonResponse({"success": True, "message": "Momo transaction créée avec succès"})
        
    elif "status" in data:  # FLOOZ
        # Extraire les données de la transaction Momo
        id_requete =  data["referenceID"]
        statuscode =  data["status"]
        message =  data["statusMessage"]
        numero_transaction =  data["subscriberMsisdn"]
        montant = float(data["amount"])
        reference_operateur_id = data["floozRefid"]
        operateur = data["operateur"]
        transaction_type =  data["transaction_type"]
        user_id = data["user_id"]  

        # Vérifier si l'ID de réservation correspond à une réservation existante
        try:
            reservation = Reservation.objects.get(id_reservation=id_reservation)
        except Reservation.DoesNotExist:
            reservation = None

        if reservation:
            # Créer la transaction Momo et l'associer à la réservation
            momo_transaction = Momo_transaction.objects.create(
                id_requete=id_requete,
                statuscode=statuscode,
                message=message,
                numero_transaction=numero_transaction,
                montant=montant,
                reference_operateur_id=reference_operateur_id,
                operateur=operateur,
                type=transaction_type,
                user_id=user_id,
               
            )

            # Mettre à jour le champ canal_paiement dans la réservation
            reservation.statut_paiement = True
            reservation.canal_paiement = "Momo Transaction"
            reservation.transaction_type = ContentType.objects.get_for_model(Momo_transaction)
            reservation.transaction_id = momo_transaction.id_requete
            reservation.save()

            # Renvoyer une réponse JSON avec le statut de création
            return JsonResponse({"success": True, "message": "Momo transaction créée avec succès"})
        try:
            utilisateur = Utilisateur.objects.get(id=int(id_reservation))
        except Utilisateur.DoesNotExist:
            utilisateur = None

        if utilisateur:
            # Mettre à jour le portefeuille de l'utilisateur avec le montant de la transaction
            utilisateur.portefeuille += montant
            utilisateur.save()
            # Créer la transaction Momo sans association à une réservation
            momo_transaction = Momo_transaction.objects.create(
                id_requete=id_requete,
                statuscode=statuscode,
                message=message,
                numero_transaction=numero_transaction,
                montant=montant,
                reference_operateur_id=reference_operateur_id,
                operateur=operateur,
                type=transaction_type,
                user_id=user_id,
            )

            # Renvoyer une réponse JSON avec le statut de création
            return JsonResponse({"success": True, "message": "Momo transaction créée avec succès"})
        
    # Si la transaction n'a pas été créée ou l'ID de réservation est invalide, renvoyer une réponse JSON avec un statut d'échec
    return JsonResponse({"success": False, "message": "Échec de la création de la momo transaction"})

            
#Liste des Momo_transactions
def get_momo_transaction(request):
    data = { "momo_transactions": [] }
    momo_transactions = Momo_transaction.objects.all()
    for momo_transaction in momo_transactions:
        data["momo_transactions"].append({
            "id_requete": momo_transaction.id_requete,
            "montant": momo_transaction.montant,
            "statuscode": momo_transaction.statuscode,
            "message": momo_transaction.message,
            "date": momo_transaction.date,
            "montant": momo_transaction.montant,
            "numero_transaction": momo_transaction.numero_transaction,
            "user_id": momo_transaction.user_id,
            "reference_operateur_id": momo_transaction.reference_operateur_id,
            "operateur": momo_transaction.operateur,
            "type": momo_transaction.type
                       
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data)            

#Infos des Momo transaction par utilisateurs et par ordre recent
def get_momo_transactions_by_user(request, user_id):
    transactions = Momo_transaction.objects.filter(user_id=user_id).order_by('-date')
    
    data = {
        "transactions": []
    }
    
    for transaction in transactions:
        data["transactions"].append({
            "id_requete": transaction.id_requete,
            "statuscode": transaction.statuscode,
            "message": transaction.message,
            "numero_transaction": transaction.numero_transaction,
            "montant": transaction.montant,
            "reference_operateur_id": transaction.reference_operateur_id,
            "operateur": transaction.operateur,
            "type": transaction.type,
            "user_id": transaction.user_id,
            "date": transaction.date
        })
    
    return JsonResponse(data)

#Infos des Momo transaction par numero de telephone et par ordre recent
def get_momo_transactions_by_phone(request, phone_number):
    transactions = Momo_transaction.objects.filter(numero_transaction=phone_number).order_by('-date')
    
    data = {
        "transactions": []
    }
    
    for transaction in transactions:
        data["transactions"].append({
            "id_requete": transaction.id_requete,
            "statuscode": transaction.statuscode,
            "message": transaction.message,
            "numero_transaction": transaction.numero_transaction,
            "montant": transaction.montant,
            "reference_operateur_id": transaction.reference_operateur_id,
            "operateur": transaction.operateur,
            "type": transaction.type,
            "user_id": transaction.user_id,
            "date": transaction.date
        })
    
    return JsonResponse(data)
#Modification d'un Momo_transaction
@csrf_exempt
def update_momo_transaction(request, id):
    momo_transaction = get_object_or_404(Momo_transaction, id=id)
    if request.method == 'POST':
        serializer = Momo_transaction(momo_transaction, data=request.data)
        if serializer.is_valid():
            serializer.update(momo_transaction, request.data)
            return JsonResponse({"info": "momo transaction modifié"})
        return JsonResponse({"error": serializer.errors})
            


#Suppression d'un Momo_transaction
@csrf_exempt
def delete_momo_transaction(request, id):
    momo_transaction = Momo_transaction.objects.get(id=id)
    momo_transaction.delete()       
    
    
  
                                ### Fonction de la classe Reservation  ###

### Creer une Reservation
@csrf_exempt
def create_reservation(request):
    if request.method == "POST":
        data = json.loads(request.body)
        tour_id = data['tour_id']
        nb_place = data['nb_place']
        
        if 'voyageur_id' in data:
            # Cas où l'utilisateur est connecté
            voyageur_id = data['voyageur_id']
            voyageur = Voyageur.objects.get(id=voyageur_id)
        else:
            # Cas où l'internaute effectue une réservation sans être connecté
            voyageur = Voyageur.objects.create(nom_complet=data['nom_complet'], contact=data['contact'])

        serializer = reservationSerializer(data=data)
        if serializer.is_valid():
            reservation = serializer.save(voyageur_id=voyageur)

            # Générer l'identifiant de réservation unique
            id_reservation = None
            while not id_reservation:
                last_id = Reservation.objects.order_by('-id').first()
                if last_id:
                    last_id = last_id.id + 1
                else:
                    last_id = 1
                new_id_reservation = f"RESER{last_id:04d}"
                if Reservation.objects.filter(id_reservation=new_id_reservation).exists():
                    # L'identifiant existe déjà, continuer la boucle pour en générer un nouveau
                    continue
                id_reservation = new_id_reservation
            
            # Assigner l'identifiant de réservation à la réservation créée
            reservation.id_reservation = id_reservation
            reservation.save()

            tour = Tour.objects.get(id=tour_id)
            tour.nb_reservation += nb_place
            tour.save()

            return JsonResponse({"message":"success","Info": "Réservation créée", "id_reservation": reservation.id_reservation})
        else:
            return JsonResponse({"message":"error","Info": "Réservation non créée", "errors": serializer.errors})

    return JsonResponse({"Info": "Requête invalide"})


 

            
#Liste des Reservations
def get_reservation(request):
    data = { "reservations": [] }
    reservations = Reservation.objects.all()
    for reservation in reservations:
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None
        data["reservations"].append({
            "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id.id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "nb_place": reservation.nb_place,
            "date": reservation.date,
            "tour_id": reservation.tour_id.id,
            "tour_libelle": reservation.tour_id.libelle,
            "latitude_pickup": reservation.latitude_pickup,
            "longitude_pickup": reservation.longitude_pickup,
            "statut": reservation.statut_paiement,
            "canal_paiement": reservation.canal_paiement,
            "transaction_type": transaction_type,
            "transaction_id": reservation.transaction_id,
                       
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data)            
# Obtenir une réservation par son ID_reservation
def get_reservation_by_idres(request, id_reservation):
    try:
        reservation = Reservation.objects.get(id_reservation=str(id_reservation))
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None

        data = {
            "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id.id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "nb_place": reservation.nb_place,
            "tour_id": reservation.tour_id.id,
            "latitude_pickup": reservation.latitude_pickup,
            "longitude_pickup": reservation.longitude_pickup,
            "statut": reservation.statut_paiement,
            "canal_paiement": reservation.canal_paiement,
            "transaction_type": transaction_type,
            "transaction_id": reservation.transaction_id,
        }
        return JsonResponse(data)
    except Reservation.DoesNotExist:
        return JsonResponse({"error": "La réservation spécifiée n'existe pas."})


# Obtenir les réservations pour un Voyageur donné
def get_reservations_by_voyageur(request, voyageur_id):
    data = {"reservations": []}
    reservations = Reservation.objects.filter(voyageur_id=voyageur_id)
    for reservation in reservations:
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None
        
        data["reservations"].append({
           "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "nb_place": reservation.nb_place,
            "tour_id": reservation.tour_id,
            "latitude_pickup": reservation.latitude_pickup,
            "longitude_pickup": reservation.longitude_pickup,
            "statut": reservation.statut_paiement,
            "canal_paiement": reservation.canal_paiement,
            "transaction_type": transaction_type,
            "transaction_id": reservation.transaction_id,
        })
    return JsonResponse(data)

# Obtenir les réservations pour un Utilisateur donné
def get_reservations_by_utilisateur(request, utilisateur_id):
    data = {"reservations": []}
    reservations = Reservation.objects.filter(utilisateur_id=utilisateur_id)
    for reservation in reservations:
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None
        data["reservations"].append({
            "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "nb_place": reservation.nb_place,
            "tour_id": reservation.tour_id,
            "latitude_pickup": reservation.latitude_pickup,
            "longitude_pickup": reservation.longitude_pickup,
            "statut": reservation.statut_paiement,
            "canal_paiement": reservation.canal_paiement,
            "transaction_type": transaction_type,
            "transaction_id": reservation.transaction_id,
        })
    return JsonResponse(data)

#Modification d'une Reservation
@csrf_exempt
def update_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    if request.method == 'POST':
        serializer = reservationSerializer(reservation, data=request.data)
        if serializer.is_valid():
            serializer.update(reservation, request.data)
            return JsonResponse({"info": "reservation modifiée"})
        return JsonResponse({"error": serializer.errors})
            


#Suppression d'une Reservation
@csrf_exempt
def delete_reservation(request, id):
    reservation = Reservation.objects.get(id=id)
    reservation.delete()           
    
    
    
    

#Generer un token

"""   Crrer un chauffeur:
  utilisateur = Utilisateur.objects.get(id=user_id)
  chauffeur = Chauffeur.objects.create(
    user=utilisateur,
    num_permis='1234567890',
    Categorie_permis='B',
    statut='Actif'
)
 """

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajoutez des champs personnalisés au payload du token
        token['user_id'] = user.id
        token['user_email'] = user.email
        # Ajoutez d'autres champs personnalisés si nécessaire

        return token
    
    
from rest_framework_simplejwt.tokens import RefreshToken
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data['email']
        password = data['password']

        try:
            user = Utilisateur.objects.get(email=email)
            stored_password = user.password

            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                serializer = utilisateurSerializer(user)
                token = RefreshToken.for_user(user)

                role_id = None
                if user.is_voyageur:
                    role_id = Voyageur.objects.get(user_id=user.id).id
                elif user.is_fournisseur:
                    role_id = Proprietaire.objects.get(user_id=user.id).id
                elif user.is_chauffeur:
                    role_id = Chauffeur.objects.get(user_id=user.id).id

                return JsonResponse({
                    'status': 200,
                    'success': True,
                    'message': 'Connecté avec succès',
                    'nom': user.nom,
                    'prenom': user.prenom,
                    'email': user.email ,
                    'contact': user.contact,
                    'date_naiss': user.date_naissance,
                    'sexe': user.sexe,
                    'portefeuille': user.portefeuille,
                    'id': user.id,
                    'role_id': role_id,
                    'is_voyageur': user.is_voyageur,
                    'is_fournisseur': user.is_fournisseur,
                    'is_chauffeur': user.is_chauffeur,
                    'isloggenIn': True,
                    'token': {
                        'access': str(token.access_token),
                        'refresh': str(token),
                    }
                })
            else:
                return JsonResponse({
                    'status': 400,
                    'success': False,
                    'message': 'Options de connexion invalides'
                })
        except Utilisateur.DoesNotExist:
            return JsonResponse({
                'status': 400,
                'success': False,
                'message': 'Options de connexion invalides'
            })
 
 
@csrf_exempt
def adminlogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data['email']
        password = data['password']

        admin = Administrateur.objects.get(email=email)
        admin_stored_password = admin.password

        if bcrypt.checkpw(password.encode('utf-8'), admin_stored_password.encode('utf-8')):
            serializer = administrateurSerializer(admin)
            token = RefreshToken.for_user(admin)

            return JsonResponse({
                'status': 200,
                'success': True,
                'message': 'Connecté avec succès',
                'nom': admin.nom,
                'email': admin.email ,
                'contact': admin.contact,
                'token': {
                    'access': str(token.access_token),
                    'refresh': str(token),
                }
            })
        else:
            return JsonResponse({
                'status': 400,
                'success': False,
                'message': 'Options de connexion invalides'
            })

 