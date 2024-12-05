from django.urls import path
from django.conf.urls.static import static
from befit_app import settings
from django.conf import settings
from . import views
from django_q.tasks import schedule
from django.contrib.auth import views as auth_views
from .views import (
    admin_dashboard, cancel_reservation, affiche_workout, coach_dashboard, 
    delete_draft, delete_message, mark_important, send_message, messages_inbox, 
    subscribe, subscription_list, validate_username, validate_password, profile, 
    edit_profile, workout_list, subscription, contact_coach, contact_member, 
    add_workout_schedule, remind_subscription, workout_detail, download_invoice,
    service_detail, register_user, change_password, reset_user_password, add_review,
    conditions_vente, cookies, confidentialite, mentions_legales, 
    cookie_consent_view, banner_view, cookie_preferences_view, coach_availabilities,
)

urlpatterns = [
    # Pages statiques
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),

    # Accueil et recherche
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),

    # Authentification
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Profil
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),

   # Dashboard du coach
    path('coach_dashboard/', views.coach_dashboard, name='coach_dashboard'),
    path('new_workoutSchedule/', views.add_workout_schedule, name='newWorkoutSchedule'),
    path('get_schedule_details/<int:schedule_id>/', views.get_schedule_details, name='get_schedule_details'),
    path('new_workout_schedule/<int:schedule_id>/', views.add_workout_schedule, name='editWorkoutSchedule'),
    path('coach_scheduled_sessions/', views.coach_scheduled_sessions, name='coach_scheduled_sessions'),


    # Disponibilités des coachs
    path('coach_availabilities/', views.coach_availabilities, name='coach_availabilities'),
    path('toggle_coach_availability/<int:coach_id>/', views.toggle_coach_availability, name='toggle_coach_availability'),

    # Gestion des demandes
    path('submit_request/', views.submit_request, name='submit_request'),
    path('view_requests/', views.view_requests, name='view_requests'),
    # Gestion des demandes
    path('update_request_status/<int:coach_id>/<str:status>/', views.update_session_request_status, name='update_request_status'),

    # Tableau de bord admin
    path('admin_reports/', views.admin_reports, name='admin_reports'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    

    # Contact
    path('contact_coach/<int:coach_id>/', contact_coach, name='contact_coach'),  
    path('contact_member/<int:member_id>/', contact_member, name='contact_member'),

    # Messages
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

    # Plans & Abonnement
    path('plan/<int:pk>/', views.plan, name='plan'),
    path('remind_subscription/<int:user_id>/', views.remind_subscription, name='remind_subscription'),
    path('subscription/<int:pk>/', views.subscribe, name='subscription'),
    path('subscriptions/', subscription_list, name='subscription_list'),
    path('subscribe/<int:pk>/', subscribe, name='subscribe'),
    path('get-product-price/<int:service_id>/', views.get_product_price, name='get_product_price'),
    path('download_invoice/<int:purchase_id>/', views.download_invoice, name='download_invoice'),

    # Services & Entraînements
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
    path('confirmation_reservation/<int:scheduleId>/', views.confirmation_reservation, name='confirmation_reservation'),
    path('add-review/<int:workout_id>/', views.add_review, name='add_review'),

    # Conditions légales et politique de confidentialité
    path('conditions-de-vente/', views.conditions_vente, name='conditions_vente'),
    path('cookies_privacy/', views.cookies, name='cookies'),
    path('politique-confidentialite/', views.confidentialite, name='confidentialite'),
    path('mentions-legales/', views.mentions_legales, name='mentions_legales'),

    # Cookie consent
    path('cookie/', views.cookie_consent_view, name='cookie_consent'),
    path('banner/', views.banner_view, name='banner'),
    path('preferences/', views.cookie_preferences_view, name='cookie_preferences'),

    # URL supplémentaires
    

]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
