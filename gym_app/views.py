import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from gym_app.models import CatalogService, Coach, DietPlan, GymAccessory, Message, PersonalizedCoaching, Plan, Review, Subscription, Workout, WorkoutImage, WorkoutSchedule, WorkoutParticipation
from .forms import SignUpForm, UserProfileForm, WorkoutParticipationForm
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta
from django.urls import path
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import TruncMonth, ExtractHour
from django_q.tasks import schedule
from django_q.tasks import async_task





User = get_user_model()

# Vue pour la page à propos


def about(request):
    return render(request, 'about.html')

# Vue pour la page d'accueil


def home(request):
    plans = Plan.objects.filter(is_available=True)
    workouts = Workout.objects.filter(available=True)
    coachs = Coach.objects.all()
    reviews = Review.objects.all()
    workoutschedules = WorkoutSchedule.objects.select_related('coach', 'location').all()

    # Ajouter les services du catalogue
    catalog_services = CatalogService.objects.filter(is_available=True)
    personalized_coaching = PersonalizedCoaching.objects.all()
    gym_accessories = GymAccessory.objects.all()
    diet_plans = DietPlan.objects.all()

    return render(request, 'home.html', {
        'plans': plans,
        'workouts': workouts,
        'coachs': coachs,
        'reviews': reviews,
        'workoutschedules': workoutschedules,
        'catalog_services': catalog_services,
        'personalized_coaching': personalized_coaching,
        'gym_accessories': gym_accessories,
        'diet_plans': diet_plans,
    })

# Vue pour la page FAQ


def faq(request):
    return render(request, 'faq.html')


# Notification pour relancer abonnement arriver a echeance
@login_required
def remind_subscription(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        subscription = get_object_or_404(Subscription, user=user, payment_status='pending')

        # Créez un message de relance
        subject = "Relance d'abonnement"
        body = f"Bonjour {user.get_full_name()}, votre abonnement est en attente. " \
               f"Veuillez le renouveler ou envisager notre offre de 12 mois - Evolve."

        # Enregistrer le message de notification dans la base de données
        Message.objects.create(
            sender=request.user,
            recipient=user,
            subject=subject,
            body=body,
            is_read=False
        )

        # Notification réussie
        messages.success(request, f'La relance a été envoyée à {user.get_full_name()}.')

        return redirect('coach_dashboard')

    return HttpResponseForbidden("Méthode non autorisée.")





# Configuration de la clé secrète Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Liste des abonnements
def subscription_list(request):
    plans = Plan.objects.filter(is_available=True)
    return render(request, 'subscription_list.html', {'plans': plans})

# Détails d'une souscription
def subscription(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk)
    return render(request, 'subscription.html', {'subscription': subscription})

# Souscription Abonnement


@login_required
def subscribe(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        # Créer une nouvelle souscription pour l'utilisateur connecté
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            payment_status='pending'
        )
        # Rediriger vers une page de paiement (à implémenter)
        return redirect('payment', subscription.id)
    return render(request, 'subscription.html', {'plan': plan})

# Vue pour créer une session Stripe et démarrer le paiement
@login_required
def create_checkout_session(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    # Créer une session de paiement Stripe
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': plan.name,
                },
                'unit_amount': plan.price * 100,  # Prix en centimes
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/payment/success/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/payment/cancel/'),
    )

    # Sauvegarder le plan dans la session pour l'utilisateur
    request.session['plan_id'] = plan.id

    return JsonResponse({
        'id': checkout_session.id
    })

# Gestion du succès du paiement
@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == 'paid':
        plan_id = request.session.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id)

        # Créer une souscription pour l'utilisateur
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            payment_status='paid',
        )
        
        # Mettre à jour l'utilisateur en premium
        request.user.is_premium = True
        request.user.save()

        # Supprimer le plan de la session
        del request.session['plan_id']

        return render(request, 'payment_success.html', {'plan': plan})

    return render(request, 'payment_failed.html')



# Gestion du succès du paiement
@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == 'paid':
        plan_id = request.session.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id)

        # Créer une souscription pour l'utilisateur
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            payment_status='paid',
        )
        
        # Mettre à jour l'utilisateur en premium
        request.user.is_premium = True
        request.user.save()

        # Supprimer le plan de la session
        del request.session['plan_id']

        return render(request, 'payment_success.html', {'plan': plan})

    return render(request, 'payment_failed.html')

# Gestion de l'annulation du paiement
@login_required
def payment_cancel(request):
    return render(request, 'payment_cancel.html')

# Mise à jour du statut premium de l'utilisateur
def update_premium_status(user):
    current_subscription = Subscription.objects.filter(
        user=user, end_date__gt=timezone.now()).first()
    if current_subscription and current_subscription.plan.is_premium:
        user.is_premium = True
    else:
        user.is_premium = False
    user.save()

# Vue pour la page d'abonnement spécifique


def plan(request, pk):
    plan = get_object_or_404(Plan, id=pk)
    return render(request, 'plan.html', {'plan': plan})

# Vue pour la connexion utilisateur


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue, {user.username}!')
            return redirect('home')
        else:
            messages.error(
                request, 'Nom d\'utilisateur ou mot de passe incorrect')
            return render(request, 'administration/login.html')
    else:
        return render(request, 'administration/login.html')

# Vue pour la déconnexion utilisateur


def logout_user(request):
    user = request.user
    logout(request)
    messages.success(request, f'Aurevoir et à bientôt, {user.username}!')
    return redirect('home')

# Vue pour l'inscription d'un nouvel utilisateur


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, f'Vous êtes maintenant inscrit, {user.username}!')
                return redirect('home')
        else:
            messages.error(request, 'Erreur lors de l\'inscription')
            return redirect('register')
    else:
        form = SignUpForm()
    return render(request, 'administration/register.html', {'form': form})

@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if request.method == 'POST':
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            body=body
        )
        messages.success(request, "Votre message a été envoyé.")
        return redirect('profile')  # Rediriger vers le profil ou une autre page
    return render(request, 'send_message.html', {'recipient': recipient})


@login_required
def inbox(request):
    messages_received = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'inbox.html', {'messages': messages_received})

@login_required
def messages_inbox(request):
    # Récupérer les messages reçus par l'utilisateur
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')  # Utilisation de 'timestamp' au lieu de 'date_sent'
    
    # Comptabiliser les messages non lus
    unread_messages = messages.filter(is_read=False).count()

    context = {
        'messages': messages,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'messages_inbox.html', context)


@login_required
def base_view(request):
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'base.html', {'unread_messages': unread_messages})


@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    return render(request, 'message_detail.html', {'message': message})



@receiver(post_save, sender=User)
def create_or_update_coach(sender, instance, created, **kwargs):
    if hasattr(instance, 'role') and instance.role == 'coach':
        Coach.objects.update_or_create(
            user=instance,
            defaults={
                'username': instance.username,
                # Assure-toi que l'image est un attribut de User si nécessaire
                'image': getattr(instance, 'image', None)
            }
        )
    else:
        Coach.objects.filter(user=instance).delete()


def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    images = WorkoutImage.objects.filter(workout=pk)
    reviews = Review.objects.filter(workout = pk)
    return render(request, 'workout.html', {'workout': workout, 'images': images, 'reviews':reviews})

# Vue pour valider le nom d'utilisateur


def validate_username(request):
    username = request.GET.get('username', '')
    is_taken = User.objects.filter(username=username).exists()
    return JsonResponse({'is_taken': is_taken})

# Vue pour valider le mot de passe


def validate_password(request):
    password = request.GET.get('password', '')
    conditions = [
        len(password) >= 8,
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(not c.isalnum() for c in password)
    ]
    return JsonResponse({'conditions': conditions})


@login_required
def profile(request):
    user = request.user
    unread_messages = Message.objects.filter(recipient=user, is_read=False).count()

    # Récupérer le staff (si disponible)
    staff_id = User.objects.filter(is_staff=True).first().id if user.role == 'member' else None

    # Récupérer les séances passées avec ce coach (si l'utilisateur est un coach ou admin)
    # if user.is_staff or user.role == 'coach':
    #     member_sessions = WorkoutSchedule.objects.filter(coach=user).prefetch_related('participants')
    #     total_sessions = member_sessions.count()
    #     members_with_sessions = member_sessions.values('participants__first_name', 'participants__last_name', 'participants__email', 'participants__is_premium').distinct()
    # else:
    #     total_sessions = 0
    #     members_with_sessions = None

    # Récupérer les messages de la boîte de réception
    messages = Message.objects.filter(recipient=user).order_by('-timestamp')

    context = {
        'user': user,
        'unread_messages': unread_messages,
        'messages': messages,
        'staff_id': staff_id,
        # 'total_sessions': total_sessions,
        # 'members_with_sessions': members_with_sessions,
    }

    return render(request, 'profile.html', context)




@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Votre profil a été mis à jour avec succès.')
            return redirect('profile')
        else:
            messages.error(
                request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = UserProfileForm(instance=user)

    context = {
        'form': form,
        'user': user
    }
    return render(request, 'edit_profile.html', context)

@receiver(post_save, sender=User)
def create_coach_profile(sender, instance, created, **kwargs):
    if not created:  # Si l'utilisateur existe déjà
        if instance.role == 'coach':
            Coach.objects.get_or_create(user=instance)
@login_required
def coach_dashboard(request):
    # Vérifier si l'utilisateur est un coach ou un administrateur (is_staff)
    if request.user.role != 'coach' and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    user = request.user

    # Récupérer toutes les séances gérées par le coach connecté ou par les administrateurs
    if user.is_staff:
        schedules = WorkoutSchedule.objects.all().order_by('-start_time')
    else:
        schedules = WorkoutSchedule.objects.filter(coach=user).order_by('-start_time')

    # Récupérer les membres et leurs abonnements
    members = User.objects.filter(is_staff=False).order_by('-date_joined')  # Pour récupérer les membres
    subscriptions = Subscription.objects.select_related('user', 'plan').order_by('-start_date')

    # Récupérer les séances passées avec ce coach
    if user.is_staff or user.role == 'coach':
        member_sessions = WorkoutSchedule.objects.prefetch_related('participants').filter(coach=user)
        total_sessions = member_sessions.count()
        members_with_sessions = member_sessions.values(
            'participants__first_name', 
            'participants__last_name', 
            'participants__email', 
            'participants__is_premium'
        ).distinct()
    else:
        total_sessions = 0
        members_with_sessions = None

    # Récupérer les autres coachs sauf le coach connecté
    coaches = Coach.objects.exclude(user=request.user).select_related('user').order_by('-user__date_joined')

    # Statistiques des séances
    stats = []
    for schedule in schedules:
        total_participants = schedule.participants.count()
        present_count = WorkoutParticipation.objects.filter(workout_schedule=schedule, present=True).count()
        stats.append({
            'schedule': schedule,
            'total_participants': total_participants,
            'present_count': present_count,
            'absence_count': total_participants - present_count,
        })

    # Passer toutes les données au template
    return render(request, 'coach_dashboard.html', {
        'stats': stats,
        'members': members,
        'subscriptions': subscriptions,
        'coaches': coaches,
        'total_sessions':  total_sessions,
        'members_with_sessions': members_with_sessions,
    })



@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")

    # Récupérer les coachs et les membres
    coaches = Coach.objects.select_related('user').order_by('-user__date_joined')
    members = User.objects.filter(is_staff=False).order_by('-date_joined')

    # Récupérer les abonnements
    subscriptions = Subscription.objects.select_related('user', 'plan').order_by('-start_date')

    # Récupérer les statistiques des séances
    schedules = WorkoutSchedule.objects.all()
    stats = []
    total_participants = 0
    total_present = 0
    for schedule in schedules:
        participant_count = schedule.participants.count()
        present_count = WorkoutParticipation.objects.filter(workout_schedule=schedule, present=True).count()
        total_participants += participant_count
        total_present += present_count
        stats.append({
            'schedule': schedule,
            'total_participants': participant_count,
            'present_count': present_count,
            'absence_count': participant_count - present_count,
        })

    # Calcul du taux d'inscription par mois
    current_month = timezone.now().month
    total_members = members.count()
    monthly_new_members = members.filter(date_joined__month=current_month).count()
    if total_members > 0:
        monthly_registration_percentage = (monthly_new_members / total_members) * 100
    else:
        monthly_registration_percentage = 0

    # Calcul du taux de participation
    if total_participants > 0:
        attendance_percentage = (total_present / total_participants) * 100
    else:
        attendance_percentage = 0

    # Calcul du taux d'occupation des séances entre 7h et 19h
    total_schedules = schedules.count()
    busy_hours_schedules = schedules.filter(start_time__hour__gte=7, start_time__hour__lt=19).count()
    if total_schedules > 0:
        busy_hours_percentage = (busy_hours_schedules / total_schedules) * 100
    else:
        busy_hours_percentage = 0

    # Calcul des heures les plus fréquentées entre 7h et 19h
    busy_hour_counts = {}
    for hour in range(7, 19):
        busy_hour_counts[hour] = schedules.filter(start_time__hour=hour).count()

    # Déterminer l'heure avec le plus de participants
    most_frequent_hour = max(busy_hour_counts, key=busy_hour_counts.get)
    most_frequent_hour_count = busy_hour_counts[most_frequent_hour]

    # Calcul des plans les plus achetés
    plan_counts = subscriptions.values('plan__name').annotate(count=Count('plan')).order_by('-count')
    total_subscriptions = subscriptions.count()
    plan_percentages = []
    if total_subscriptions > 0:
        for plan in plan_counts:
            plan_percentages.append({
                'plan_name': plan['plan__name'],
                'percentage': (plan['count'] / total_subscriptions) * 100
            })

    # Calcul des séances de workout les plus fréquentées
    workout_frequencies = schedules.values('workout__title').annotate(count=Count('workout')).order_by('-count')
    workout_percentages = []
    if total_schedules > 0:
        for workout in workout_frequencies:
            workout_percentages.append({
                'workout_title': workout['workout__title'],
                'percentage': (workout['count'] / total_schedules) * 100
            })

    # Calcul du taux de séances par coach
    coach_schedule_counts = schedules.values('coach__first_name', 'coach__last_name').annotate(count=Count('coach')).order_by('-count')
    coach_percentages = []
    if total_schedules > 0:
        for coach in coach_schedule_counts:
            coach_percentages.append({
                'coach_name': f"{coach['coach__first_name']} {coach['coach__last_name']}",
                'percentage': (coach['count'] / total_schedules) * 100
            })

    context = {
        'coaches': coaches,
        'members': members,
        'subscriptions': subscriptions,
        'stats': stats,
        'attendance_percentage': attendance_percentage,
        'monthly_registration_percentage': monthly_registration_percentage,
        'busy_hours_percentage': busy_hours_percentage,
        'plan_percentages': plan_percentages,
        'workout_percentages': workout_percentages,
        'coach_percentages': coach_percentages,
        'busy_hour_counts': busy_hour_counts,
        'most_frequent_hour': most_frequent_hour,
        'most_frequent_hour_count': most_frequent_hour_count,
    }

    return render(request, 'admin_dashboard.html', context)



@login_required
def contact_coach(request, coach_id):
    coach = get_object_or_404(User, id=coach_id)

    if request.method == 'POST':
        message_body = request.POST.get('message')
        Message.objects.create(
            sender=request.user,
            recipient=coach,
            subject=f"Nouveau message de {request.user.get_full_name()}",
            body=message_body
        )
        messages.success(request, f"Message envoyé à {coach.get_full_name()}")
        return redirect('coach_dashboard')

    return HttpResponseForbidden("Action non autorisée")

@login_required
def contact_member(request, member_id):
    member = get_object_or_404(User, id=member_id)
    if request.method == 'POST':
        message = request.POST.get('message')
        send_mail(
            subject=f"Message de {request.user.get_full_name()}",
            message=message,
            from_email=request.user.email,
            recipient_list=[member.email],
            fail_silently=False,
        )
        return HttpResponseRedirect(reverse('admin_dashboard'))


@login_required
def affiche_workout(request, workout_id):
    start_of_week = timezone.now().date(
    ) - timedelta(days=timezone.now().weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)

    weekly_schedules = WorkoutSchedule.objects.filter(
        workout_id=workout_id,
        # Filtrer par la semaine actuelle
        start_time__date__range=[start_of_week, end_of_week],
        start_time__gte=timezone.now()  # Exclure les séances déjà passées
    )
    workout = get_object_or_404(Workout, id=workout_id)
    images = WorkoutImage.objects.filter(workout=workout_id)

    return render(request, 'reserve_workout.html', {
        'weekly_schedules': weekly_schedules,
        'workout': workout,
        'images': images,
    })


def workout_list(request):
    # Récupère tous les workouts, vous pouvez filtrer selon vos besoins
    workouts = Workout.objects.all()
    return render(request, 'workout_list.html', {'workouts': workouts})


@login_required
def cancel_reservation(request, workoutschedule_id):
    user = request.user
    booking = get_object_or_404(WorkoutSchedule, id=workoutschedule_id)

    if booking.start_time > timezone.now() + timedelta(hours=24):
        booking.participants.remove(user)
        messages.success(request, "Votre séance a bien été annulée.")
    else:
        messages.error(request, "Vous ne pouvez annuler une réservation que 24h avant la séance.")

    return redirect('profile')


@login_required
def confirmation_reservation(request, scheduleId):
    # Récupérer le planning de workout avec l'ID fourni
    schedule = get_object_or_404(WorkoutSchedule, id=scheduleId)

    # Vérifier si la séance est complète
    if schedule.participants.count() >= 10:
        messages.error(
            request, "Cette séance est complète. Vous ne pouvez plus réserver.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    # Vérifier si l'utilisateur est déjà participant
    if schedule.participants.filter(id=request.user.id).exists():
        messages.error(request, "Vous avez déjà réservé cette séance.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    # Ajouter l'utilisateur à la liste des participants
    schedule.participants.add(request.user)
    schedule.save()

    messages.success(request, "Votre réservation a été confirmée avec succès.")
    return redirect('home')

@login_required
def manage_participation(request, workout_schedule_id):
    workout_schedule = get_object_or_404(WorkoutSchedule, id=workout_schedule_id)
    participants = workout_schedule.participants.all()
    
    # Crée des instances de WorkoutParticipation pour chaque participant si elles n'existent pas déjà
    for participant in participants:
        WorkoutParticipation.objects.get_or_create(
            workout_schedule=workout_schedule, 
            participant=participant
        )
    
    participations = WorkoutParticipation.objects.filter(workout_schedule=workout_schedule)
    
    if request.method == 'POST':
        for participation in participations:
            form = WorkoutParticipationForm(request.POST, instance=participation)
            if form.is_valid():
                form.save()
        return redirect('manage_participation', workout_schedule_id=workout_schedule.id)

    return render(request, 'manage_participation.html', {
        'workout_schedule': workout_schedule,
        'participations': participations,
    })

@login_required
def add_review(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id)
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            Review.objects.create(
                user=request.user,
                workout=workout,
                content=contenu
            )
            messages.success(request, "Votre avis a été ajouté avec succès.")
        else:
            messages.error(request, "Le contenu du commentaire ne peut pas être vide.")
    
    # Redirection vers la page 'workout_detail'
    return redirect('workout_detail', pk=workout.id)

def conditions_vente(request):
    return render(request, 'conditions_vente.html')

def cookies(request):
    return render(request, 'cookies.html')

def confidentialite(request):
    return render(request, 'confidentialite.html')

def mentions_legales(request):
    return render(request, 'mentions_legales.html')
