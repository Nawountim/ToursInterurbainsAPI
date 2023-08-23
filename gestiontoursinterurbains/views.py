from django.shortcuts import render
from django.http import JsonResponse
from .models import Utilisateur, Vehicule,Administrateur, Trajet, Tour, Reservation, Chauffeur, Voyageur, Proprietaire, Momo_transaction, Wallet_transaction
from .serializers import utilisateurSerializer,administrateurSerializer, proprietaireSerializer, vehiculeSerializer, trajetSerializer, voyageurSerializer, tourSerializer, momoTransactionSerializer, walletTransactionSerializer, reservationSerializer, chauffeurSerializer
import json
from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime
from collections import defaultdict
import calendar
import json
import requests
import time
from django.views.decorators.http import require_GET
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
from django.db.models import F
from django.core.mail import send_mail
from django.db.models import Count, Sum
from datetime import datetime, date
from django.conf import settings



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
        login(data)
    return redirect("/get_utilisateur")



        

            
#Liste des utilisateurs
def get_utilisateur(request):
    data = { "utilisateurs": [] }
    utilisateurs = Utilisateur.objects.all().order_by('-id')
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
    if request.method == 'PATCH':
        data = json.loads(request.body)
        serializer = utilisateurSerializer(utilisateur, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Utilisez serializer.save() pour enregistrer les modifications
            return JsonResponse({"info": "utilisateur modifié","status":200})
        return JsonResponse({"error": serializer.errors,"status":400})
    return JsonResponse({"info": "Modification effectuée"})


#Suppression d'un utilisateur
@csrf_exempt
def delete_utilisateur(request, id):
    try:
        # Vérification de l'existence de l'utilisateur
        utilisateur = Utilisateur.objects.get(id=id)

        # Vérification et suppression dans la classe "Voyageur"
        voyageur = Voyageur.objects.filter(user_id=utilisateur)
        if voyageur.exists():
            voyageur.delete()

        # Vérification et suppression dans la classe "Proprietaire"
        proprietaire = Proprietaire.objects.filter(user_id=utilisateur)
        if proprietaire.exists():
            proprietaire.delete()

        # Vérification et suppression dans la classe "Chauffeur"
        chauffeur = Chauffeur.objects.filter(user_id=utilisateur)
        if chauffeur.exists():
            chauffeur.delete()

        # Suppression de l'utilisateur
        utilisateur.delete()

        return JsonResponse({"message": "Utilisateur supprimé", "code": 200})

    except Utilisateur.DoesNotExist:
        return JsonResponse({"message": "Utilisateur introuvable", "code": 404})
    except Exception as e:
        return JsonResponse({"message": "Utilisateur non supprimé", "code": 500})

    
                                ###  Fonction de la classe Propriétaire  ###
@csrf_exempt                            
def create_proprietaire(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update_id = data['user_id']
        proprietaire_serializer = proprietaireSerializer(data=data)
        
        if proprietaire_serializer.is_valid():
            proprietaire_instance = proprietaire_serializer.save()  # Sauvegarde du voyageur créé
            proprietaire_id = proprietaire_instance.id
            utilisateur = update_id  # Récupération de l'ID de l'utilisateur associé au voyageur
            utilisateur_obj = Utilisateur.objects.get(id=utilisateur)  # Récupération de l'objet utilisateur complet
            
            utilisateur_obj.is_fournisseur = True  # Mise à jour du champ is_voyageur à True
            utilisateur_obj.save()  # Sauvegarde de l'utilisateur modifié
            
            return JsonResponse({"Info": "Proprietaire créé", 'status':200, 'role_id': proprietaire_id})
        else:
            return JsonResponse({"Info": "Proprietaire non créé", 'status':400})
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
                            
@csrf_exempt                            
def create_voyageur(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update_id = data.get('user_id')
        
        try:
            utilisateur_obj = Utilisateur.objects.get(id=update_id)
        except ObjectDoesNotExist:
            return JsonResponse({"Info": "Utilisateur avec cet ID n'existe pas.", 'status':400})
        
        # Create a data dictionary for voyageurSerializer with user_id and nom_complet
        voyageur_data = {
            'user_id': update_id,
            'nom_complet': f"{utilisateur_obj.nom} {utilisateur_obj.prenom}",
            'contact' : utilisateur_obj.contact
        }
        
        voyageur_serializer = voyageurSerializer(data=voyageur_data)
        
        if voyageur_serializer.is_valid():
            voyageur_instance =voyageur_serializer.save()  # Sauvegarde du voyageur créé
            voyageur_id = voyageur_instance.id
               
            
            utilisateur_obj.is_voyageur = True  # Mise à jour du champ is_voyageur à True
            utilisateur_obj.save()  # Sauvegarde de l'utilisateur modifié
            
            return JsonResponse({"Info": "Voyageur créé", 'status':200, 'role_id': voyageur_id})
        else:
            return JsonResponse({"Info": "Voyageur non créé", "errors": voyageur_serializer.errors, 'status':400})
    
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
            chauffeur_instance = serializer.save()
            chauffeur_id = chauffeur_instance.id
                            
            utilisateur = update_id  # Récupération de l'ID de l'utilisateur associé au voyageur
            utilisateur_obj = Utilisateur.objects.get(id=utilisateur)  # Récupération de l'objet utilisateur complet
            
            utilisateur_obj.is_chauffeur = True  # Mise à jour du champ is_voyageur à True
            utilisateur_obj.save()  # Sauvegarde de l'utilisateur modifié
            
            return JsonResponse({"Info": "chauffeur créé", 'status': 200, 'role_id': chauffeur_id})
        else:
         #return JsonResponse({"error": serializer.errors})
         return JsonResponse({"Info":"chauffeur non créé", 'status': 400})
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
            "contact": chauffeur.user_id.contact,
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
        serializer = chauffeurSerializer(chauffeur, data=request.data, partial=True)
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

        return JsonResponse({"info": "Statut de disponibilité modifié", "code":200})

    return JsonResponse({"error": "Statut de disponibilité non autorisé", "code":400})


#Suppression d'un chauffeur
@csrf_exempt
def delete_chauffeur(request, id):
    chauffeur = get_object_or_404(Chauffeur, id=id)
    
     # Vérifier si le véhicule est affecté à des tours
    if chauffeur.tour_set.exists():
        # Si le véhicule est lié à des tours, renvoyer une réponse indiquant qu'il ne peut pas être supprimé
        return JsonResponse({'message': 'Ce Chauffeur est affecté à des tours et ne peut pas être encore supprimé.', 'status': 400})

    chauffeur.delete()  
    
    return HttpResponse({'message':'Chauffeur supprimé avec succès.','status':200})                                                        

 
### Creer un trajet
@csrf_exempt
def create_trajet(request):
    if request.method == "POST":
        data = json.loads(request.body)
        serializer = trajetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Trajet créé", "code":200})
        else:
         #return JsonResponse({"error": serializer.errors})
         return JsonResponse({"message":"Trajet non créé", "code":400})
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
            "start_longitude": trajet.start_longitude,
            "start_latitude": trajet.start_latitude,
            "end_longitude": trajet.end_longitude,
            "end_latitude": trajet.end_latitude,
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data)            


#Modification d'un trajet
@csrf_exempt
def update_trajet(request, id):
    trajet = get_object_or_404(Trajet, id=id)
    if request.method == 'POST':
        serializer = trajetSerializer(trajet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(trajet, request.data)
            return JsonResponse({"info": "trajet modifié"})
        return JsonResponse({"error": serializer.errors})
            


#Suppression d'un trajet
@csrf_exempt
def delete_trajet(request, id):
    trajet = get_object_or_404(Trajet, id=id)  
    if trajet.tour_set.exists():
        # Si le véhicule est lié à des tours, renvoyer une réponse indiquant qu'il ne peut pas être supprimé
        return JsonResponse({'message': 'Ce Trajet est affecté à des tours et ne peut pas être encore supprimé.', 'status': 400})

    trajet.delete()    
    return HttpResponse({'message':'Trajet supprimé avec succès.','status':200}) 

    
def delete_chauffeur(request, id):
    chauffeur = get_object_or_404(Chauffeur, id=id)
    
     # Vérifier si le véhicule est affecté à des tours
    if chauffeur.tour_set.exists():
        # Si le véhicule est lié à des tours, renvoyer une réponse indiquant qu'il ne peut pas être supprimé
        return JsonResponse({'message': 'Ce Chauffeur est affecté à des tours et ne peut pas être encore supprimé.', 'status': 400})

    chauffeur.delete()  
    
    return HttpResponse({'message':'Chauffeur supprimé avec succès.','status':200}) 
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
                "proprietaire": vehicule.proprietaire_id.user_id.nom
            })
    
    return JsonResponse(data)



#Vehicule  acceptés
def get_vehicules_acceptes(request):
    data = {"vehicules_acceptes": []}
    vehicules = Vehicule.objects.filter(is_accepted=True)

    for vehicule in vehicules:
        vehicule_data = {
            "id": vehicule.id,
            "marque": vehicule.marque,
            "visite_technique": vehicule.visite_technique,
            "plaque": vehicule.plaque,
            "statut": vehicule.statut,
            "is_accepted": vehicule.is_accepted,
            "nb_place": vehicule.nb_place,
            "proprietaire_id": vehicule.proprietaire_id.id,
            "proprietaire": vehicule.proprietaire_id.user_id.nom
        }

        data["vehicules_acceptes"].append(vehicule_data)

    return JsonResponse(data)


#Vehicule non acceptés
def get_vehicules_non_acceptes(request):
    data = {"vehicules_non_acceptes": []}
    vehicules = Vehicule.objects.filter(is_accepted=False)

    for vehicule in vehicules:
        vehicule_data = {
            "id": vehicule.id,
            "marque": vehicule.marque,
            "visite_technique": vehicule.visite_technique,
            "plaque": vehicule.plaque,
            "statut": vehicule.statut,
            "is_accepted": vehicule.is_accepted,
            "nb_place": vehicule.nb_place,
            "proprietaire_id": vehicule.proprietaire_id.id,
            "proprietaire": vehicule.proprietaire_id.user_id.nom
        }

        data["vehicules_non_acceptes"].append(vehicule_data)

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
                "is_accepted": vehicule.is_accepted,
                "nb_place": vehicule.nb_place,
                "proprietaire_id": vehicule.proprietaire_id.id,
                "proprietaire": vehicule.proprietaire_id.user_id.nom
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
                "proprietaire": vehicule.proprietaire_id.user_id.nom
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
                "proprietaire": vehicule.proprietaire_id.user_id.nom
            })
        return JsonResponse(data)
    except Vehicule.DoesNotExist:
        return JsonResponse({"error": "Aucun véhicule trouvé pour le propriétaire spécifié."})
    
#Liste des véhicules par propriétaire et leur tours assignés    
def get_vehicules_tours(request, id):
    try:
        vehicule = Vehicule.objects.get(id=id)
        data = {
            "vehicule": []
        }

        tours_assigned = Tour.objects.filter(vehicule_id=id)
        tours_data = []

        for tour in tours_assigned:
            tours_data.append({
                "id_tour": tour.id_tour,
                "libelle": tour.libelle,
                "date": tour.date,
                "heure": tour.heure,
                "statut": tour.statut,
                "chauffeur": tour.chauffeur_id.user_id.nom if tour.chauffeur_id else None,
                "trajet": tour.trajet_id.libelle if tour.trajet_id else None,
                "capacite": tour.capacite,
            })

        data["vehicule"].append({
            "id": vehicule.id,
            "marque": vehicule.marque,
            "visite_technique": vehicule.visite_technique,
            "plaque": vehicule.plaque,
            "statut": vehicule.statut,
            "is_accepted": vehicule.is_accepted,
            "nb_place": vehicule.nb_place,
            "proprietaire_id": vehicule.proprietaire_id.id,
            "proprietaire": vehicule.proprietaire_id.user_id.nom,
            "tours_assigned": tours_data,
        })

        return JsonResponse(data)
    except Vehicule.DoesNotExist:
        return JsonResponse({"error": "Aucun véhicule trouvé avec l'ID spécifié."})

    
#Modification d'un Vehicule
@csrf_exempt
def update_vehicule(request, id):
    vehicule = get_object_or_404(Vehicule, id=id)
    if request.method == 'POST':
        serializer = vehiculeSerializer(vehicule, data=request.data, partial=True)
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
    vehicule = get_object_or_404(Vehicule, id=id)

    # Vérifier si le véhicule est affecté à des tours
    if vehicule.tour_set.exists():
        # Si le véhicule est lié à des tours, renvoyer une réponse indiquant qu'il ne peut pas être supprimé
        return JsonResponse({'message': 'Ce véhicule est affecté à des tours et ne peut pas être supprimé.', 'status': 400})

    # Si le véhicule n'est lié à aucun tour, vous pouvez le supprimer en toute sécurité
    vehicule.delete()

    return HttpResponse({'message':'Véhicule supprimé avec succès.','status':200})  
    
    
     

                                ### Fonction de la classe Tour  ###

### Creer un Tour
@csrf_exempt
def create_tour(request):
    if request.method == "POST":
        data = json.loads(request.body)
        chauffeur_id = data['chauffeur_id']
        date = data['date']
        heure = data['heure']
        libelle = data['libelle']
        vehicule_id = data['vehicule_id']
        trajet_id = data['trajet_id']
        serializer = tourSerializer(data=data)
        try:
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
        except Chauffeur.DoesNotExist:
                return JsonResponse({"message": "Le chauffeur spécifié n'existe pas.", "code": 404})

        try:
                vehicule = Vehicule.objects.get(id=vehicule_id)
        except Vehicule.DoesNotExist:
                return JsonResponse({"message": "Le véhicule spécifié n'existe pas.", "code": 404})

        try:
                trajet = Trajet.objects.get(id=trajet_id)
        except Trajet.DoesNotExist:
                return JsonResponse({"message": "Le trajet spécifié n'existe pas.", "code": 404})


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
            
            # Envoyer un email au chauffeur
            """ 
            send_mail(
                subject="Vous avez été affecté à une nouvelle tournée",
                message=r"Cher {chauffeur.user_id.nom} {chauffeur.user_id.prenom},\n\n Vous avez été affecté à la tournée : {libelle}.\n\n Cordialement,\n Notre nom d'entreprise",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[chauffeur.user_id.email],
                fail_silently=False,
            )

            # Sending email to the vehicle owner
            send_mail(
                subject="Votre véhicule a été affecté à une nouvelle tournée",
                message=r"Cher propriétaire du véhicule,\n\n Votre véhicule {vehicule.marque} a été affecté à la tournée  : {libelle}.\n\n Cordialement,\nNotre nom d'entreprise",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[vehicule.proprietaire_id.user_id.email],
                fail_silently=False,
            ) """

            return JsonResponse({"message": "Tour créé", "code": 200 })
        else:
         #return JsonResponse({"error": serializer.errors})
            return JsonResponse({"message":"Serializer invalide" , "code": 400})
    return redirect("/get_tour")   

 
@csrf_exempt
def tour_effectuer(request, id):
    t = get_object_or_404(Tour, id=id)

    if request.method == 'POST':
        data = json.loads(request.body)
        statut = data['statut']
       
        if statut is None:
            return JsonResponse({"error": "Statut manquant"})

        if statut == 'true':
            t.statut = True
        elif statut == 'false':
            t.statut = False
        else:
            return JsonResponse({"error": "Statut invalide"})

        t.save()

        return JsonResponse({"info": "Tour effectué", "code": 200})

    return JsonResponse({"error": "Modification du statut non autorisé", "code": 400})

            
#Liste des Tours actifs
def get_tour(request):
    data = { "tours": [] }
    tours = Tour.objects.all().filter(statut=True).order_by('-id')

    for tour in tours:
        data["tours"].append({
            "id": tour.id,
           "libelle": tour.libelle,
            "prix": tour.prix,
            "id_tour": tour.id_tour,
            "statut": tour.statut,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "vehicule": tour.vehicule_id.marque,
            "nb_reservation": tour.nb_reservation,
            "date": tour.date,
            "heure": tour.heure,
            "trajet_id": tour.trajet_id.id,
            "trajet": tour.trajet_id.libelle,
            "capacite": tour.capacite,
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data) 
   
#Liste de tous les tours
def get_all_tours(request):
    data = { "tours": [] }
    tours = Tour.objects.all().order_by('-id')

    for tour in tours:
        data["tours"].append({
            "id": tour.id,
           "libelle": tour.libelle,
            "prix": tour.prix,
            "id_tour": tour.id_tour,
            "statut": tour.statut,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "vehicule": tour.vehicule_id.marque,
            "nb_reservation": tour.nb_reservation,
            "date": tour.date,
            "heure": tour.heure,
            "trajet_id": tour.trajet_id.id,
            "trajet": tour.trajet_id.libelle,
            "capacite": tour.capacite,
                                  })
        """ Envoyer sous forme de Json: API """
    return JsonResponse(data) 




#Liste des Tours disponible(nb_place > 0)
def get_tour_disponible(request):
    data = { "tours": [] }

    # Sélectionner les tours où nb_reservation est inférieur à capacité
    tours = Tour.objects.filter(nb_reservation__lt=F('capacite'), statut = True).order_by('-date')

    for tour in tours:
        data["tours"].append({
            "id": tour.id,
            "libelle": tour.libelle,
            "id_tour": tour.id_tour,
             "prix": tour.prix,
            "statut": tour.statut,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "vehicule": tour.vehicule_id.marque,
            "nb_reservation": tour.nb_reservation,
            "date": tour.date,
            "heure": tour.heure,
            "trajet_id": tour.trajet_id.id,
            "trajet": tour.trajet_id.libelle,
            "capacite": tour.capacite,
        })

    # Envoyer sous forme de JSON : API
    return JsonResponse(data)   

#Avoir un tour
def get_one_tour(request, id):
    try:
        tour = Tour.objects.get(id=id)
        data = {
            "id": tour.id,
            "libelle": tour.libelle,
            "id_tour": tour.id_tour,
             "prix": tour.prix,
            "statut": tour.statut,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "vehicule": tour.vehicule_id.marque,
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
            "prix": tour.prix,
            "chauffeur_id": tour.chauffeur_id.id,
            "chauffeur_nom": tour.chauffeur_id.user_id.nom,
            "vehicule_id": tour.vehicule_id.id,
            "vehicule": tour.vehicule_id.marque,
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
                "prix": tour.prix,
                "statut": tour.statut,
                "chauffeur_id": tour.chauffeur_id.id,
                "chauffeur_nom": tour.chauffeur_id.user_id.nom, 
                "vehicule": tour.vehicule_id.marque,
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
                 "prix": tour.prix,
                "statut": tour.statut,
                "chauffeur_id": tour.chauffeur_id.id,
                "chauffeur_nom": tour.chauffeur_id.user_id.nom,
                "vehicule_id": tour.vehicule_id.id,
                "vehicule": tour.vehicule_id.marque,
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
    wallet_transactions = Wallet_transaction.objects.all().order_by('-id')
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
            "reservation_idres": wallet_transaction.reservation_id.id_reservation,
            "nom_reservant": wallet_transaction.reservation_id.voyageur_id.nom_complet,
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
            "nom_reservant": transaction.reservation_id.voyageur_id.nom_complet,
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
            "reservation_idres": transaction.reservation_id.id_reservation,
            "date": transaction.date,
            "nom_reservant": transaction.reservation_id.voyageur_id.nom_complet,
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
        serializer = Wallet_transaction(wallet_transaction, data=request.body, partial=True)
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
    #id_service peut etre celui d'une reservation ou d'un utilisateurs
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
        if statuscode == "2002":

            # Vérifier si l'ID de réservation correspond à une réservation existante
            try:
                reservation = Reservation.objects.get(id_reservation=id_reservation)
            except Reservation.DoesNotExist:
                reservation = None

            if reservation:
                # Créer la transaction Momo et l'associer à la réservation
            
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
        if statuscode == "0":

            # Vérifier si l'ID de réservation correspond à une réservation existante
            try:
                reservation = Reservation.objects.get(id_reservation=id_reservation)
            except Reservation.DoesNotExist:
                reservation = None

            if reservation:
                # Créer la transaction Momo et l'associer à la réservation
            
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
            

                # Renvoyer une réponse JSON avec le statut de création
                return JsonResponse({"success": True, "message": "Momo transaction créée avec succès"})
        
    # Si la transaction n'a pas été créée ou l'ID de réservation est invalide, renvoyer une réponse JSON avec un statut d'échec
    return JsonResponse({"success": False, "message": "Échec de la création de la momo transaction"})


@csrf_exempt
def send_tmoney_transaction(request):
    # Charger les données JSON à partir du corps de la requête
    data = json.loads(request.body)
    
    # Exemple d'URL de destination
    destination_url = "https://pay.suisco.net/api/push-ussd/tmoney/request"
    
    try:
        id_requete = data["idRequete"]
        numero_transaction = data["numeroClient"]
        montant = float(data["montant"])
        user_id = data["user_id"]
        
        # Création de la transaction d'abord
        transaction = Momo_transaction.objects.create(
            id_requete=id_requete,
            numero_transaction=numero_transaction,
            montant=montant,
            operateur="TMONEY",
            type="DEBIT",
            user_id=user_id,
        )
        
        # Supprimer le champ user_id du dictionnaire data avant d'envoyer la requête
        if "user_id" in data:
            del data["user_id"]
        
        # Ensuite, effectuer la requête HTTP POST vers l'URL de destination
        print(data)
        response = requests.post(destination_url, json=data)
        response_json = response.json()
    
        code = response_json["code"]
        statut_requete = response_json.get("statutRequete")
        ref_operateur_id = response_json.get("refTmoney")
        
        transaction.statuscode = code
        transaction.message = statut_requete
        transaction.reference_operateur_id = ref_operateur_id
        transaction.save()
        
        if code == "2002":
            try:
                user = Utilisateur.objects.get(id=user_id)
                user.portefeuille += montant
                user.save()
                
            except Utilisateur.DoesNotExist:
                # Gérer le cas où l'utilisateur n'est pas trouvé
                pass

        return JsonResponse({"status": "success", "code": code, "message": statut_requete})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"status": "error", "message": "Une erreur s'est produite lors de la communication avec le serveur : {}".format(e), "code": 400})

""" @csrf_exempt    
def long_polling_view(request):
    while True:
        if has_updates():
            updates = get_updates()
            return JsonResponse(updates)
        time.sleep(2) """
        

@csrf_exempt
def send_flooz_transaction(request):
    # Charger les données JSON à partir du corps de la requête
    data = json.loads(request.body)
    
    # Supprimer le champ user_id du dictionnaire data s'il est présent
    
    
    # Exemple d'URL de destination
    destination_url = "https://pay.suisco.net/api/push-ussd/flooz/request"
    
    try:
        id_requete = data["transactionCode"]
        numero_transaction = data["destMobileNumber"]
        montant = float(data["amount"])
        user_id = data.get("user_id", None)  # Récupérer user_id s'il est présent
        
        # Création de la transaction d'abord
        transaction = Momo_transaction.objects.create(
            id_requete=id_requete,
            numero_transaction=numero_transaction,
            montant=montant,
            operateur="FLOOZ",
            type="DEBIT",
            user_id=user_id,
        )
        
        # Supprimer le champ user_id du dictionnaire data avant d'envoyer la requête
        if "user_id" in data:
            del data["user_id"]
        
        # Ensuite, effectuer la requête HTTP POST vers l'URL de destination
        print(data)
        response = requests.post(destination_url, json=data)
        response_json = response.json()
        
        status = response_json["status"]
        status_message = response_json.get("statusMessage")
        ref_operateur_id = response_json.get("floozRefid")
        
        transaction.statuscode = status
        transaction.message = status_message
        transaction.reference_operateur_id = ref_operateur_id
        transaction.save()
        
        if status == "0":
            # Gérer le succès de la transaction, par exemple, mise à jour du portefeuille utilisateur
            try:
                user = Utilisateur.objects.get(id=user_id)
                user.portefeuille += montant
                user.save()
                
            except Utilisateur.DoesNotExist:
                # Gérer le cas où l'utilisateur n'est pas trouvé
                pass
        
        return JsonResponse({"status": status, "message": status_message})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"status": "error", "message": "Une erreur s'est produite lors de la communication avec le serveur : {}".format(e), "code": 400})

                        
#Liste des Momo_transactions
def get_momo_transaction(request):
    data = { "momo_transactions": [] }
    momo_transactions = Momo_transaction.objects.all().order_by('-id')
    
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
        serializer = Momo_transaction(momo_transaction, data=request.body, partial=True)
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
    reservations = Reservation.objects.all().order_by('-id')
    for reservation in reservations:
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None
        data["reservations"].append({
            "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id.id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "nb_place": reservation.nb_place,  
            "prix": reservation.prix,         
            "date": reservation.date,
            "tour_date": reservation.tour_id.date,
            "tour_heure": reservation.tour_id.heure,
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
            "prix": reservation.prix, 
            "date": reservation.date,
            "tour_id": reservation.tour_id.id,
            "tour_statut": reservation.tour_id.statut,
            "tour_libelle": reservation.tour_id.libelle,
            "tour_date": reservation.tour_id.date,
            "tour_heure": reservation.tour_id.heure,
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
    
    
def get_reservation_itineraire(request, id_reservation):
    try:
        reservation = Reservation.objects.get(id_reservation=str(id_reservation))
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None

        data = {
            "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id.id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "nb_place": reservation.nb_place,
            "prix": reservation.prix, 
            "date": reservation.date,
            "tour_id": reservation.tour_id.id,
            "tour_libelle": reservation.tour_id.libelle,
            "tour_statut": reservation.tour_id.statut,
            "trajet": reservation.tour_id.trajet_id.libelle,
            "trajet_distance": reservation.tour_id.trajet_id.distance,
            "trajet_start_longitude": reservation.tour_id.trajet_id.start_longitude,
            "trajet_start_latitude": reservation.tour_id.trajet_id.start_latitude,
            "trajet_end_longitude": reservation.tour_id.trajet_id.end_longitude,
            "trajet_end_latitude": reservation.tour_id.trajet_id.end_latitude,
            "tour_date": reservation.tour_id.date,
            "tour_heure": reservation.tour_id.heure,
            "latitude_pickup": reservation.latitude_pickup,
            "longitude_pickup": reservation.longitude_pickup,

        }
        return JsonResponse(data)
    except Reservation.DoesNotExist:
        return JsonResponse({"error": "La réservation spécifiée n'existe pas."})
    
    
# Obtenir les réservations pour un tour donné
def get_reservations_by_tour(request, tour_id):
    try:
        reservations = Reservation.objects.filter(tour_id=tour_id).order_by('-id')
        data = []
        for reservation in reservations:
            transaction_type = reservation.transaction_type.model if reservation.transaction_type else None

            reservation_data = {
                "id": reservation.id,
                "id_reservation": reservation.id_reservation,
                "voyageur_id": reservation.voyageur_id.id,
                "voyageur_nom": reservation.voyageur_id.nom_complet,
                "nb_place": reservation.nb_place,
                "prix": reservation.prix, 
                "tour_id": reservation.tour_id.id,
                "tour_date": reservation.tour_id.date,
                 "tour_heure": reservation.tour_id.heure,
                 "date": reservation.date,
                "latitude_pickup": reservation.latitude_pickup,
                "longitude_pickup": reservation.longitude_pickup,
                "statut": reservation.statut_paiement,
                "canal_paiement": reservation.canal_paiement,
                "transaction_type": transaction_type,
                "transaction_id": reservation.transaction_id,
            }
            data.append(reservation_data)

        return JsonResponse(data, safe=False)
    except Tour.DoesNotExist:
        return JsonResponse({"error": "Le tour spécifié n'existe pas."})
    
    
# Obtenir les réservations pour un Voyageur donné
def get_reservations_by_voyageur(request, voyageur_id):
    data = {"reservations": []}
    reservations = Reservation.objects.filter(voyageur_id=voyageur_id).order_by('-id')
    for reservation in reservations:
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None
        
        data["reservations"].append({
           "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id.id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "nb_place": reservation.nb_place,
            "prix": reservation.prix, 
            "tour_id": reservation.tour_id.id,
            "tour_statut": reservation.tour_id.statut,
            "date": reservation.date,
            "tour_date": reservation.tour_id.date,
            "tour_heure": reservation.tour_id.heure,
            "libelle_tour": reservation.tour_id.libelle,
            "trajet": reservation.tour_id.trajet_id.libelle,
            "latitude_pickup": reservation.latitude_pickup,
            "longitude_pickup": reservation.longitude_pickup,
             "Heure_depart": reservation.tour_id.heure,
            "statut": reservation.statut_paiement,
            "canal_paiement": reservation.canal_paiement,
            "transaction_type": transaction_type,
            "transaction_id": reservation.transaction_id,
        })
    return JsonResponse(data)

# Obtenir les réservations pour un Utilisateur donné
def get_reservations_by_utilisateur(request, utilisateur_id):
    data = {"reservations": []}
    reservations = Reservation.objects.filter(utilisateur_id=utilisateur_id).order_by('-id')
    for reservation in reservations:
        transaction_type = reservation.transaction_type.model if reservation.transaction_type else None
        data["reservations"].append({
            "id": reservation.id,
            "id_reservation": reservation.id_reservation,
            "voyageur_id": reservation.voyageur_id,
            "voyageur_nom": reservation.voyageur_id.nom_complet,
            "prix": reservation.prix, 
            "nb_place": reservation.nb_place,
            "tour_id": reservation.tour_id,
            "tour_date": reservation.tour_id.date,
            "tour_heure": reservation.tour_id.heure,
             "tour_statut": reservation.tour_id.statut,
             "Heure": reservation.tour_id.heure,
             "date": reservation.date,
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
        serializer = reservationSerializer(reservation, data=request.body, partial=True)
        if serializer.is_valid():
            serializer.update(reservation, request.data)
            return JsonResponse({"info": "reservation modifiée"})
        return JsonResponse({"error": serializer.errors})
            


#Suppression d'une Reservation
@csrf_exempt
def delete_reservation(request, id):
    try:
        reservation = Reservation.objects.get(id=id) 
        print(reservation.tour_id)   
        tour = Tour.objects.get(id=reservation.tour_id.id)
        tour.nb_reservation -= reservation.nb_place  # Soustraire le nombre de places réservées
        tour.save()  # Enregistrez les modifications du nombre de réservations sur le tour
        reservation.delete()  # Supprimez la réservation
        return JsonResponse({"message": "Reservation annulée", "code": 200})
    except Reservation.DoesNotExist:
        return JsonResponse({"message": "La réservation n'existe pas", "code": 404})
    except Tour.DoesNotExist:
        return JsonResponse({"message": "Le tour associé à la réservation n'existe pas", "code": 404})
    
    
    

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
                    'message': 'Mot de passe incorrect'
                })
        except Utilisateur.DoesNotExist:
            return JsonResponse({
                'status': 400,
                'success': False,
                'message': 'L\'email fourni n\'existe pas'
            })
 
from django.core.exceptions import ObjectDoesNotExist 
@csrf_exempt
def adminlogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data['email']
        password = data['password']

        try:
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
                    'email': admin.email,
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
                    'message': 'Mot de passe incorrect'
                })
        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 404,
                'success': False,
                'message': 'L\'email fourni n\'existe pas'
            })

 
#LES STATISTIQUES

def trajets_plus_empruntes(request):
    trajets = Trajet.objects.all()
    data = [{'libelle': trajet.libelle, 'nombre_utilisation': trajet.nombre_emprunts()} for trajet in trajets]
    return JsonResponse({'trajets': data}, safe=False)


""" def trajets_plus_empruntes(request):
    trajets = Trajet.objects.annotate(nb_emprunts=Count('tour'))
    data = [{'libelle': trajet.libelle, 'nb_emprunts': trajet.nb_emprunts} for trajet in trajets]
    return JsonResponse({'trajets': data}, safe=False)

 """

def vehicules_plus_utilises():
    vehicules = Vehicule.objects.annotate(nb_utilisations=Count('tour')).order_by('-nb_utilisations')
    return vehicules


""" def chauffeurs_plus_sollicites(request):
    chauffeurs = Chauffeur.objects.all()
    data = [{'Nom': chauffeur.user_id.nom, 'nombre_utilisation': chauffeur.nombre_utilisation()} for chauffeur in chauffeurs]
    return JsonResponse({'chauffeurs': data}, safe=False)
 """
 
def chauffeurs_plus_sollicites(request):
    # Obtenir les chauffeurs et le nombre d'utilisations
    chauffeurs = Chauffeur.objects.annotate(
        nombre_utilisation=Count('tour')
    ).order_by('-nombre_utilisation')[:3]

    # Créer une liste de dictionnaires contenant les informations des chauffeurs
    chauffeurs_list = []
    for chauffeur in chauffeurs:
        chauffeur_info = {
            'Nom': chauffeur.user_id.nom,
            'nombre_utilisation': chauffeur.nombre_utilisation,
        }
        chauffeurs_list.append(chauffeur_info)

    # Retourner les informations des chauffeurs au format JSON
    return JsonResponse({'chauffeurs': chauffeurs_list}, safe=False)

@csrf_exempt
def rendements_utilisateurs(request):
    rendements = []  # Initialisez une liste vide pour stocker les données finales

    if request.method == 'POST':
        data = json.loads(request.body)
        date_debut = data['date_debut']
        date_fin = data['date_fin']
        try:
            # Récupérez les rendements à partir de Wallet_transaction
            wallet_rendements = Wallet_transaction.objects.filter(date__range=(date_debut, date_fin)).values('user_id').annotate(total_rendements=Sum('montant'))
            
            # Créez un dictionnaire pour stocker les rendements cumulés par user_id
            rendements_cumules = defaultdict(float)

            # Pour chaque rendement, récupérez l'utilisateur correspondant et ajoutez les rendements cumulés
            for item in wallet_rendements:
                user_id = item['user_id']
                utilisateur = Utilisateur.objects.get(id=user_id)
                rendement = item['total_rendements']
                rendements_cumules[user_id] += rendement

            # Récupérez également les données de Momo_transaction
            momo_data = Momo_transaction.objects.filter(date__range=(date_debut, date_fin))  # Ajoutez la logique appropriée pour récupérer les données de Momo_transaction

            # Ajoutez les données de Momo_transaction aux rendements cumulés
            for momo_item in momo_data:
                utilisateur = Utilisateur.objects.get(id=momo_item.user_id)
                rendement = momo_item.montant
                rendements_cumules[momo_item.user_id] += rendement

            # Transformez le dictionnaire de rendements cumulés en une liste
            for user_id, rendement_cumule in rendements_cumules.items():
                utilisateur = Utilisateur.objects.get(id=user_id)
                rendements.append({
                    'user_id': utilisateur.id,
                    'nom': utilisateur.nom,
                    'prenom': utilisateur.prenom,
                    'voyageur': utilisateur.is_voyageur,
                    'fournisseur': utilisateur.is_fournisseur,
                    'chauffeur': utilisateur.is_chauffeur,
                    'rendement_cumule': rendement_cumule
                })

            return JsonResponse({'rendements': rendements}, safe=False)
        except Exception as e:
            # Gérer l'exception, par exemple, imprimer un message d'erreur
            print(f"Erreur : {str(e)}")
    
    return JsonResponse({'rendements': rendements}, safe=False)


def rendements_utilisateurs_jour(request):
    rendements = []  # Initialisez une liste vide pour stocker les données finales

    # Utilisez la date actuelle comme date de début et de fin
    date_actuelle = timezone.now().date()

    try:
        # Récupérez les rendements à partir de Wallet_transaction
        wallet_rendements = Wallet_transaction.objects.filter(date__date=date_actuelle).values('user_id').annotate(total_rendements=Sum('montant'))
        
        # Créez un dictionnaire pour stocker les rendements cumulés par user_id
        rendements_cumules = defaultdict(float)

        # Pour chaque rendement, récupérez l'utilisateur correspondant et ajoutez les rendements cumulés
        for item in wallet_rendements:
            user_id = item['user_id']
            utilisateur = Utilisateur.objects.get(id=user_id)
            rendement = item['total_rendements']
            rendements_cumules[user_id] += rendement

        # Récupérez également les données de Momo_transaction
        momo_data = Momo_transaction.objects.filter(date__date=date_actuelle)  # Ajoutez la logique appropriée pour récupérer les données de Momo_transaction

        # Ajoutez les données de Momo_transaction aux rendements cumulés
        for momo_item in momo_data:
            utilisateur = Utilisateur.objects.get(id=momo_item.user_id)
            rendement = momo_item.montant
            rendements_cumules[momo_item.user_id] += rendement

        # Transformez le dictionnaire de rendements cumulés en une liste
        for user_id, rendement_cumule in rendements_cumules.items():
            utilisateur = Utilisateur.objects.get(id=user_id)
            rendements.append({
                'user_id': utilisateur.id,
                'nom': utilisateur.nom,
                'prenom': utilisateur.prenom,
                'voyageur': utilisateur.is_voyageur,
                'fournisseur': utilisateur.is_fournisseur,
                'chauffeur': utilisateur.is_chauffeur,
                'rendement_cumule': rendement_cumule
            })

        return JsonResponse({'rendements': rendements}, safe=False)
    except Exception as e:
        # Gérer l'exception, par exemple, imprimer un message d'erreur
        print(f"Erreur : {str(e)}")

    return JsonResponse({'rendements': rendements}, safe=False)


def chiffre_affaires_par_mois(request):
    try:
        # Obtenez l'année en cours
        annee_courante = date.today().year

        # Obtenez les noms des mois
        mois_labels = list(calendar.month_name)[1:]

        # Initialisez un dictionnaire pour stocker les chiffres d'affaires par mois
        chiffre_affaires_par_mois = {mois: 0 for mois in mois_labels}

        # Obtenez le chiffre d'affaires à partir de Wallet_transaction pour l'année en cours
        chiffre_affaires_wallet = (
            Wallet_transaction.objects
            .filter(date__year=annee_courante)  # Filtrez les transactions Wallet pour l'année en cours
            .values('date__month')  # Groupement par mois
            .annotate(chiffre_affaires=Sum('montant'))  # Calcul du chiffre d'affaires total pour chaque mois
        )

        # Obtenez le chiffre d'affaires à partir de Momo_transaction pour l'année en cours
        chiffre_affaires_momo = (
            Momo_transaction.objects
            .filter(date__year=annee_courante)  # Filtrez les transactions Momo pour l'année en cours
            .values('date__month')  # Groupement par mois
            .annotate(chiffre_affaires=Sum('montant'))  # Calcul du chiffre d'affaires total pour chaque mois
        )

        # Mettez à jour le dictionnaire avec les chiffres d'affaires
        for wallet_item in chiffre_affaires_wallet:
            mois = mois_labels[wallet_item['date__month'] - 1]  # L'indice de mois commence à 1
            chiffre_affaires_par_mois[mois] += wallet_item['chiffre_affaires']

        for momo_item in chiffre_affaires_momo:
            mois = mois_labels[momo_item['date__month'] - 1]
            chiffre_affaires_par_mois[mois] += momo_item['chiffre_affaires']

        # Convertissez le dictionnaire en une liste de tuples (mois, chiffre_affaires)
        chiffre_affaires_data = [{'mois': mois, 'chiffre_affaires': ca} for mois, ca in chiffre_affaires_par_mois.items()]

        return JsonResponse({'chiffre_affaires_par_mois': chiffre_affaires_data}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def calculate_total_transactions(request):
    # Obtenez la date actuelle pour les transactions du jour
    today = date.today()

    # Calculez le montant total des transactions Momo pour la journée
    momo_total = Momo_transaction.objects.filter(date__date=today).aggregate(Sum('montant'))['montant__sum'] or 0.0

    # Calculez le montant total des transactions Wallet pour la journée
    wallet_total = Wallet_transaction.objects.filter(date__date=today).aggregate(Sum('montant'))['montant__sum'] or 0.0

    # Calculez le montant total des deux types de transactions
    total_amount = momo_total + wallet_total

    response_data = {
        'total_amount': total_amount
    }

    return JsonResponse(response_data)

   

 
@csrf_exempt
def getPaygatTransactionResponse(request):
    if request.method == "POST":
        data = json.loads(request.body)
    
        return JsonResponse({"data": data, "code": 200})
    
@csrf_exempt
def sendPaygatTransaction(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        # Les données à envoyer à l'URL externe
        
        
        external_url = "https://paygateglobal.com/api/v1/pay"  # Remplacez par l'URL externe cible
        
        try:
            response = requests.post(external_url, json=data)
            
            
            return JsonResponse({"response": response})
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({"status": "error", "message": "Une erreur s'est produite lors de la communication avec le serveur externe : {}".format(e)})

    return JsonResponse({"status": "error", "message": "Méthode non autorisée."})
    
@csrf_exempt
def sendPaygatTransactionTest(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
       