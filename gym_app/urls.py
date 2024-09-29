from django.urls import path
from django.conf.urls.static import static
from befit_app import settings
from .views import (cancel_reservation, payment, affiche_workout, subscribe, subscription_list, validate_username, validate_password, profile, edit_profile, workout_list, subscription)
from gym_app import views





urlpatterns = [
    
    
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('plan/<int:pk>', views.plan, name='plan'),
    path('subscription/<int:pk>/', views.subscribe, name='subscription'),
    path('subscriptions/', subscription_list, name='subscription_list'),
    path('subscribe/<int:pk>/', subscribe, name='subscribe'),
    path('payment/<int:subscription_id>/', payment, name='payment'),
    path('payment_success/<int:subscription_id>/', views.payment_success, name='payment_success'),
    path('register/', views.register_user, name='register'),
    path('workout/<int:pk>/', views.workout_detail, name='workout_detail'),
    path('validate_username/', validate_username, name='validate_username'),
    path('validate_password/', validate_password, name='validate_password'),
    path('reserve/<int:workout_id>/', views.affiche_workout, name='affiche_workout'),
    path('cancel_reservation/<int:workoutschedule_id>/', cancel_reservation, name='cancel_reservation'),
    path('workout_list/', views.workout_list, name='workout_list'),  
    path('subscription/', views.subscription, name='subscription'),  # Si nécessaire
    path('confirmation_reservation/<int:scheduleId>/', views.confirmation_reservation, name='confirmation_reservation'),
    path('add-review/<int:workout_id>/', views.add_review, name='add_review'),

    path('conditions-de-vente/', views.conditions_vente, name='conditions_vente'),
    path('politique-cookies/', views.cookies, name='cookies'),
    path('politique-confidentialite/', views.confidentialite, name='confidentialite'),
    path('mentions-legales/', views.mentions_legales, name='mentions_legales'),



    
] 


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) : 
# Cette ligne permet de servir les fichiers médias (comme les images téléchargées) pendant le développement lorsque le mode debug est activé.

# if settings.DEBUG: : Cela garantit que les fichiers médias sont uniquement servis par Django lorsque vous êtes en mode développement.
#  En production, un serveur web comme Nginx ou Apache s'occupera de cette tâche.