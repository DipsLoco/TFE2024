from django.urls import path
from django.conf.urls.static import static
from befit_app import settings
from .views import ( admin_dashboard, cancel_reservation, affiche_workout, coach_dashboard, delete_draft, delete_message, mark_important, send_message, messages_inbox, subscribe, subscription_list, validate_username, validate_password, profile, edit_profile, workout_list, subscription, coach_dashboard, contact_coach, contact_member, add_workout_schedule, remind_subscription)
from gym_app import views
from django_q.tasks import schedule
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views









urlpatterns = [
    
    
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('coach_dashboard/', views.coach_dashboard, name='coach_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('contact_coach/<int:coach_id>/', contact_coach, name='contact_coach'),  
    path('contact_member/<int:member_id>/', contact_member, name='contact_member'),
    path('archive_message/<int:message_id>/', views.archive_message, name='archive_message'),
    path('messages/mark_important/<int:message_id>/', views.mark_important, name='mark_important'),
    path('messages/drafts/', views.drafts, name='drafts'),
    path('delete_draft/<int:draft_id>/', delete_draft, name='delete_draft'),
    path('messages/delete-multiple/', views.delete_multiple_messages, name='delete_multiple_messages'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('message/restore/<int:message_id>/', views.restore_message, name='restore_message'),
    path('messages/send/<int:recipient_id>/', views.send_message, name='send_message'),
    path('messages/read/<int:message_id>/', views.read_message, name='read_message'),
    path('messages/inbox/', views.messages_inbox, name='messages_inbox'),
    path('plan/<int:pk>', views.plan, name='plan'),
    path('remind_subscription/<int:user_id>/', views.remind_subscription, name='remind_subscription'),
    path('subscription/<int:pk>/', views.subscribe, name='subscription'),
    path('subscriptions/', subscription_list, name='subscription_list'),
    path('subscribe/<int:pk>/', subscribe, name='subscribe'),
    path('download_invoice/<int:purchase_id>/', views.download_invoice, name='download_invoice'),
    path('service/<int:catalog_service_id>/', views.service_detail, name='service_detail'),
    path('register/', views.register_user, name='register'),
    path('change-password/', views.change_password, name='change_password'),
    path('reset-user-password/', views.reset_user_password, name='reset_user_password'),
    path('workout/<int:pk>/', views.workout_detail, name='workout_detail'),
    path('workout-schedule/add/', views.add_workout_schedule, name='add_workout_schedule'),
    path('validate_username/', validate_username, name='validate_username'),
    path('validate_password/', validate_password, name='validate_password'),
    path('reserve/<int:workout_id>/', views.affiche_workout, name='affiche_workout'),
    path('cancel_reservation/<int:workoutschedule_id>/', cancel_reservation, name='cancel_reservation'),
    path('workout_list/', views.workout_list, name='workout_list'),  
    path('subscription/', views.subscription, name='subscription'),  # Si nécessaire
    path('confirmation_reservation/<int:scheduleId>/', views.confirmation_reservation, name='confirmation_reservation'),
    path('add-review/<int:workout_id>/', views.add_review, name='add_review'),

    path('conditions-de-vente/', views.conditions_vente, name='conditions_vente'),
    path('cookies_privacy/', views.cookies, name='cookies'),
    path('politique-confidentialite/', views.confidentialite, name='confidentialite'),
    path('mentions-legales/', views.mentions_legales, name='mentions_legales'),
    path('new_workoutSchedule/', views.add_workout_schedule, name='newWorkoutSchedule'),
    path('get_schedule_details/<int:schedule_id>/', views.get_schedule_details, name='get_schedule_details'),
    # URL pour afficher la bannière de consentement
    path('cookie/', views.cookie_consent_view, name='cookie_consent'),
    path('banner/', views.banner_view, name='banner'),

   


    # URL pour afficher et gérer les préférences de cookies
    path('preferences/', views.cookie_preferences_view, name='cookie_preferences'),


] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) : 
# permet de servir les fichiers médias (comme les images téléchargées) pendant le développement lorsque le mode debug est activé.

# if settings.DEBUG: : Cela garantit que les fichiers médias sont uniquement servis par Django lorsque je suis en mode développement.
#  En production, un serveur web comme Nginx ou Apache s'occupera de cette tâche.