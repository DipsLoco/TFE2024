from datetime import timedelta
from pyexpat.errors import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import Subscription, Message, User
from django_q.tasks import schedule
from django.contrib.auth.decorators import login_required
from .models import Message, User
from .models import WorkoutSchedule, Message
from django.contrib.auth.models import User


def send_workout_reminder():
    # Récupérer les séances dans les 6 heures à venir
    now = timezone.now()
    upcoming_schedules = WorkoutSchedule.objects.filter(
        start_time__range=[now, now + timedelta(hours=6)]
    )

    for schedule in upcoming_schedules:
        # Envoyer un message à chaque participant
        for participant in schedule.participants.all():
            Message.objects.create(
                sender=User.objects.get(is_staff=True),  # Expéditeur : admin
                recipient=participant,  # Participant à la séance
                subject=f"Rappel : Séance de {schedule.workout.title}",
                body=f"Votre séance '{schedule.workout.title}' avec {schedule.coach.get_full_name()} est prévue le {schedule.start_time.strftime('%d %b %Y à %H:%M')}. Préparez-vous bien !"
            )


def send_reservation_confirmation(user_id, workout_title, workout_time):
    user = User.objects.get(id=user_id)
    Message.objects.create(
        sender=User.objects.get(is_staff=True),  # Expéditeur : un admin ou staff
        recipient=user,  # Utilisateur qui a réservé
        subject="Confirmation de réservation",
        body=f"Votre réservation pour le cours {workout_title} le {workout_time.strftime('%d %b %Y')} a été confirmée."
    )


# Ajouter la gestion des relances d'abonnement ici
@login_required
def notify_expiring_subscriptions():
    # Récupérer les abonnements arrivant à échéance dans les 7 prochains jours
    upcoming_expirations = Subscription.objects.filter(
        end_date__lte=timezone.now() + timedelta(days=7),
        payment_status='pending'
    )

    for subscription in upcoming_expirations:
        # Créer une notification pour l'utilisateur
        Message.objects.create(
            sender=None,  # Automatique
            recipient=subscription.user,
            subject="Renouvellement d'abonnement",
            body=f"Votre abonnement au plan {subscription.plan.name} arrive à expiration le {subscription.end_date}. Renouvelez-le pour continuer à profiter de nos services."
        )

        # Optionnel : Logique pour notifier les admins ou envoyer des messages spécifiques

@login_required
def remind_subscription(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Utiliser filter() pour récupérer tous les abonnements en attente
        pending_subscriptions = Subscription.objects.filter(user=user, payment_status='pending')

        if not pending_subscriptions.exists():
            messages.warning(request, f"Aucun abonnement en attente pour {user.get_full_name()}.")
            return redirect('coach_dashboard')

        # Parcourir chaque abonnement en attente et envoyer un message de relance
        for subscription in pending_subscriptions:
            subject = "Relance d'abonnement"
            body = f"Bonjour {user.get_full_name()}, votre abonnement {subscription.plan.name} est en attente. " \
                   f"Veuillez le renouveler ou envisager notre offre de 12 mois - Evolve."

            # Créer un message de relance dans la base de données
            Message.objects.create(
                sender=request.user,
                recipient=user,
                subject=subject,
                body=body,
                is_read=False
            )

        # Afficher un message de succès indiquant le nombre d'abonnements relancés
        messages.success(request, f'Relance envoyée à {user.get_full_name()} pour {pending_subscriptions.count()} abonnement(s) en attente.')

        return redirect('coach_dashboard')

    return HttpResponseForbidden("Méthode non autorisée.")

# def send_message(recipient, subject, body):
#     Message.objects.create(
#         sender=User.objects.get(is_staff=True),
#         recipient=recipient,
#         subject=subject,
#         body=body
#     )


