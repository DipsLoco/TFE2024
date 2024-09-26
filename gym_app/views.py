
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from gym_app.models import Booking, Coach, Plan, Review, Subscription, Workout, WorkoutImage, WorkoutSchedule
from .forms import BookingForm, SignUpForm, UserProfileForm
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
    bookings = Booking.objects.select_related('coach', 'location').all()
    return render(request, 'home.html', {'plans': plans, 'workouts': workouts, 'coachs': coachs, 'reviews': reviews, 'bookings': bookings})

# Vue pour la page FAQ
def faq(request):
    return render(request, 'faq.html')

# Vue pour la liste des abonnements disponibles
def subscription_list(request):
    plans = Plan.objects.filter(is_available=True)
    return render(request, 'subscription_list.html', {'plans': plans})

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

def update_premium_status(user):
    current_subscription = Subscription.objects.filter(user=user, end_date__gt=timezone.now()).first()
    if current_subscription and current_subscription.plan.is_premium:
        user.is_premium = True
    else:
        user.is_premium = False
    user.save()

def payment_success(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    return render(request, 'payment_success.html', {'subscription': subscription})

# Fonction de paiement Abonnement
def payment(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if request.method == 'POST':
        subscription.payment_status = 'paid'
        subscription.save()
        return redirect('payment_success', subscription.id)
    return render(request, 'payment.html', {'subscription': subscription})

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
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')
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
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Vous êtes maintenant inscrit, {user.username}!')
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
                'image': getattr(instance, 'image', None)  # Assure-toi que l'image est un attribut de User si nécessaire
            }
        )
    else:
        Coach.objects.filter(user=instance).delete()

def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    images = WorkoutImage.objects.filter(workout=pk)
    return render(request, 'workout.html', {'workout': workout, 'images': images})

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
    scheduleWorkout = WorkoutSchedule.objects.filter(participants = user)
    # Récupérer les abonnements actuels et passés
    current_subscription = Subscription.objects.filter(user=user, payment_status='paid').first()
    bookings = Booking.objects.filter(participants=user)
    # Préparer les données pour le template
    context = {
        'user': user,  # S'assure que l'utilisateur est bien passé au template
        'current_subscription': current_subscription,
        'bookings': bookings,
        'scheduleWorkout': scheduleWorkout,
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
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'form': form,
        'user': user
    }
    return render(request, 'edit_profile.html', context)


@login_required
def affiche_workout(request, workout_id):
    start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)
    
    weekly_schedules = WorkoutSchedule.objects.filter(
        workout_id=workout_id,
        start_time__date__range=[start_of_week, end_of_week],  # Filtrer par la semaine actuelle  
        start_time__gte=timezone.now()  # Exclure les séances déjà passées
    )
    workout = get_object_or_404(Workout, id=workout_id)
    images = WorkoutImage.objects.filter(workout=workout_id)


    # schedule = schedule_id
    # form = BookingForm(schedule)  # Passer les créneaux disponibles au formulaire

    # if schedule_id:
    #     schedule = get_object_or_404(WorkoutSchedule, id=schedule_id)

    #     # Rediriger les utilisateurs non-premium vers la page des abonnements
    #     if not request.user.is_premium:
    #         return redirect('subscription_list')

    #     if request.method == 'POST':
    #         form = BookingForm(request.POST, schedule=weekly_schedules)
    #         if form.is_valid():
    #             # Vérifier si la séance est complète
    #             if schedule.bookings.count() >= 10:
    #                 messages.error(request, "Cette séance est complète.")
    #                 return redirect('reserve_workout', schedule_id=schedule_id)

    #             # Vérifier si l'utilisateur a déjà réservé pour cette séance
    #             existing_booking = Booking.objects.filter(
    #                 schedule=schedule,
    #                 participants=request.user,
    #                 datetime=schedule.start_time
    #             ).exists()

    #             if existing_booking:
    #                 messages.error(request, "Vous avez déjà réservé pour cette séance.")
    #                 return redirect('reserve_workout', schedule_id=schedule_id)

    #             # Créer une réservation sans la sauvegarder immédiatement
    #             booking = form.save(commit=False)
    #             booking.schedule = schedule
    #             booking.coach = schedule.coach
    #             booking.location = schedule.location
    #             booking.datetime = schedule.start_time
    #             booking.created_by = request.user  # Associe l'utilisateur actuel à l'objet Booking

    #             # log avant la sauvegarde
    #             print("Enregistrement de l'objet Booking avant save()")
    #             booking.save()  # Enregistre l'objet pour générer l'ID

    #             # log après la sauvegarde pour vérifier l'ID
    #             print(f"Booking ID après save : {booking.id}")  # Vérifie que l'ID est bien généré

    #             # Ajouter l'utilisateur aux participants après la sauvegarde
    #             booking.participants.add(request.user)

    #             messages.success(request, "Réservation confirmée.")
    #             return redirect('profile')

    return render(request, 'reserve_workout.html', {
        'weekly_schedules': weekly_schedules,
        'workout':workout,
        'images':images,
        # 'schedule': schedule,
        # 'form': form
    })





def workout_list(request):
    workouts = Workout.objects.all()  # Récupère tous les workouts, vous pouvez filtrer selon vos besoins
    return render(request, 'workout_list.html', {'workouts': workouts})








@login_required
def cancel_reservation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, participants=request.user)
    
    # Vérifie si la réservation peut être annulée (au moins 1 heure avant)
    if booking.datetime > timezone.now() + timedelta(hours=1):
        booking.delete()
        booking.update_availability()
        return redirect('profile')
    else:
        return render(request, 'reservation_error.html', {'message': 'Vous ne pouvez pas annuler cette réservation.'})

@login_required
def confirmation_reservation(request, scheduleId):
    # Récupérer le planning de workout avec l'ID fourni
    schedule = get_object_or_404(WorkoutSchedule, id=scheduleId)

    # Vérifier si la séance est complète
    if schedule.participants.count() >= 10:
        messages.error(request, "Cette séance est complète. Vous ne pouvez plus réserver.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))  # Retourne à la page précédente si possible, sinon home

    # Vérifier si l'utilisateur est déjà participant
    if schedule.participants.filter(id=request.user.id).exists():
        messages.error(request, "Vous avez déjà réservé cette séance.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    # Ajouter l'utilisateur à la liste des participants
    schedule.participants.add(request.user)
    schedule.save()
    



    messages.success(request, "Votre réservation a été confirmée avec succès.")
    return redirect('home')