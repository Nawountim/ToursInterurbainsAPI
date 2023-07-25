from django.urls import path
from django.contrib import admin
from gestiontoursinterurbains import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="Tours interurbains API",
      default_version='v1',
      description=" Une API de notre application ",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
#Swagger    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
      
  
    
#GET

     
    path('get_utilisateur', views.get_utilisateur),   
    path('get_one_utilisateur/<int:id>', views.get_one_utilisateur),
    path('get_proprietaire', views.get_proprietaire),
    path('api/token/', views.MyTokenObtainPairSerializer, name='token_obtain_pair'),
    path('get_chauffeur', views.get_chauffeur),
    path('get_one_chauffeur/<int:id>', views.get_one_chauffeur), 
    path('get_one_chauffeur_by_user_id/<int:user_id>', views.get_one_chauffeur_by_user_id),
    path('get_disponible_chauffeur', views.get_disponible_chauffeur),
    path('get_nondisponible_chauffeur', views.get_nondisponible_chauffeur),
    path('get_trajet', views.get_trajet),
    path('get_vehicule', views.get_vehicule),
    path('get_vehicules_acceptes', views.get_vehicules_acceptes),
    path('get_vehicules_non_acceptes', views.get_vehicules_non_acceptes),
    path('get_disponible_vehicule', views.get_disponible_vehicule),
    path('get_one_vehicule', views.get_one_vehicule),
    path('get_vehicules_by_proprietaire/<int:proprietaire_id>', views.get_vehicules_by_proprietaire),
    path('get_tour', views.get_tour), 
    path('get_tour_disponible', views.get_tour_disponible),
    path('get_one_tour/<int:id>', views.get_one_tour),
    path('get_tour_by_idtour/<str:id_tour>', views.get_tour_by_idtour),
    path('get_tour_by_chauffeur/<int:chauffeur_id>', views.get_tour_by_chauffeur),
    path('get_tour_by_vehicule/<int:vehicule_id>', views.get_tour_by_vehicule),
    path('get_wallet_transaction', views.get_wallet_transaction),
    path('get_wallet_transactions_by_user/<int:user_id>', views.get_wallet_transactions_by_user),
    path('get_momo_transaction', views.get_momo_transaction),
    path('get_momo_transactions_by_user/<int:user_id>', views.get_momo_transactions_by_user),
    path('get_momo_transactions_by_phone/<int:phone_number>', views.get_momo_transactions_by_phone),
    path('get_reservation', views.get_reservation),
    path('get_reservation_by_idres/<str:id_reservation>', views.get_reservation_by_idres),
    path('get_reservations_by_voyageur/<int:voyageur_id>', views.get_reservations_by_voyageur),
    path('get_reservations_by_utilisateur', views.get_reservations_by_utilisateur),
    path('get_reservations_by_tour/tour/<int:tour_id>', views.get_reservations_by_tour),







    
#POST    
    
    path('create_utilisateur', views.create_utilisateur), 
    path('create_administrateur', views.create_administrateur),   
    path('create_proprietaire', views.create_proprietaire),
    path('create_voyageur', views.create_voyageur), 
    path('create_chauffeur', views.create_chauffeur),
    path('create_trajet', views.create_trajet),
    path('create_vehicule', views.create_vehicule),
    path('create_tour', views.create_tour),
    path('create_reservation', views.create_reservation),
    path('create_wallet_transaction', views.create_wallet_transaction),
    path('create_momo_transaction/<str:id_reservation>', views.create_momo_transaction),


#Update    
    
    path('update_utilisateur/<int:id>', views.update_utilisateur), 
    path('accept_vehicule/<int:id>', views.accept_vehicule),
    path('update_vehicule_availability/<int:id>', views.update_vehicule_availability), 
    path('update_chauffeur_availability/<int:id>', views.update_chauffeur_availability),

    
    
    


#Delete
   
    path('delete_utilisateur/<int:id>', views.delete_utilisateur), 
    
    
#Login
    
    path('login', views.login),  
    path('adminlogin', views.adminlogin),    

]
    
   
    

    