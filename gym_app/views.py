import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseForbidden, JsonResponse
from gym_app.models import Coach, Plan, Review, Subscription, Workout, WorkoutImage, WorkoutSchedule, WorkoutParticipation
from .forms import SignUpForm, UserProfileForm, WorkoutParticipationForm
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta
from django.urls import path



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
    bookings = WorkoutSchedule.objects.select_related(
        'coach', 'location').all()
    return render(request, 'home.html', {'plans': plans, 'workouts': workouts, 'coachs': coachs, 'reviews': reviews, 'bookings': bookings})

# Vue pour la page FAQ


def faq(request):
    return render(request, 'faq.html')


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
    scheduleWorkout = WorkoutSchedule.objects.filter(participants=user, start_time__gte=timezone.now())
    pastscheduleWorkout = WorkoutSchedule.objects.filter(participants=user, end_time__lt=timezone.now())

    # **Ajout d'une vérification si l'utilisateur peut annuler 24h avant ou plus**
    for schedule in scheduleWorkout:
        schedule.can_cancel = schedule.start_time > timezone.now() + timedelta(hours=24)


    # Récupérer les abonnements actuels et passés
    current_subscription = Subscription.objects.filter(
        user=user, payment_status='paid').first()
    # Préparer les données pour le template
    context = {
        'user': user,  # S'assure que l'utilisateur est bien passé au template
        'current_subscription': current_subscription,
        'scheduleWorkout': scheduleWorkout,
        'pastscheduleWorkout': pastscheduleWorkout,
        'is_premium': user.is_premium  # Optionnel, car user.is_premium est déjà disponible,
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

@login_required
def coach_dashboard(request):
    # Vérifier si l'utilisateur est un coach ou un administrateur (is_staff)
    if request.user.role != 'coach' and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")

    # Récupérer toutes les séances gérées par le coach connecté ou par les administrateurs
    schedules = WorkoutSchedule.objects.filter(coach=request.user).order_by('-start_time') if not request.user.is_staff else WorkoutSchedule.objects.all()

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
    
    return render(request, 'coach_dashboard.html', {'stats': stats})
# Vérifie si l'utilisateur est administrateur
def is_admin(user):
    return user.is_staff

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    # Récupérer les coachs
    coaches = Coach.objects.select_related('user').order_by('-user__date_joined')
    
    # Récupérer les membres (tous les utilisateurs sauf les coachs)
    members = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    # Récupérer les abonnements
    subscriptions = Subscription.objects.select_related('user', 'plan').order_by('-start_date')
    
    # Récupérer les statistiques des séances
    schedules = WorkoutSchedule.objects.all()
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
    
    context = {
        'coaches': coaches,
        'members': members,
        'subscriptions': subscriptions,
        'stats': stats,  # Ajout des statistiques de présence
    }
    
    return render(request, 'admin_dashboard.html', context)


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
