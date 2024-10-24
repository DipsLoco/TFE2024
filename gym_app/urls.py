from django.urls import path
from django.conf.urls.static import static
from befit_app import settings
from .views import (admin_dashboard, cancel_reservation, affiche_workout, coach_dashboard, send_message, messages_inbox, subscribe, subscription_list, validate_username, validate_password, profile, edit_profile, workout_list, subscription, coach_dashboard, contact_coach, contact_member, remind_subscription)
from gym_app import views
from django_q.tasks import schedule
from django.conf import settings
from django.conf.urls.static import static






urlpatterns = [
    
    
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('coach_dashboard/', views.coach_dashboard, name='coach_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('contact_coach/<int:coach_id>/', contact_coach, name='contact_coach'),  
    path('contact_member/<int:member_id>/', contact_member, name='contact_member'),  
    # path('messages/send/', views.send_message_default, name='send_message_default'),
    path('messages/send/<int:recipient_id>/', views.send_message, name='send_message'),
    path('messages/read/<int:message_id>/', views.read_message, name='read_message'),
    path('messages/inbox/', views.messages_inbox, name='messages_inbox'),
    path('plan/<int:pk>', views.plan, name='plan'),
    path('remind_subscription/<int:user_id>/', views.remind_subscription, name='remind_subscription'),
    path('subscription/<int:pk>/', views.subscribe, name='subscription'),
    path('subscriptions/', subscription_list, name='subscription_list'),
    path('subscribe/<int:pk>/', subscribe, name='subscribe'),
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

    # path('payment/<int:subscription_id>/', payment, name='payment'),
    path('payment_success/<int:subscription_id>/', views.payment_success, name='payment_success'),
    path('create-checkout-session/<int:plan_id>/', views.create_checkout_session, name='create_checkout_session'),

    path('new_workoutSchedule/', views.newWorkoutSchedule , name='newWorkoutSchedule'),
    
    

    

    



    
] 



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) : 
# Cette ligne permet de servir les fichiers médias (comme les images téléchargées) pendant le développement lorsque le mode debug est activé.

# if settings.DEBUG: : Cela garantit que les fichiers médias sont uniquement servis par Django lorsque vous êtes en mode développement.
#  En production, un serveur web comme Nginx ou Apache s'occupera de cette tâche.