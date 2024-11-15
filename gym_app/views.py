from difflib import get_close_matches
import json
from urllib import request
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
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
from .forms import SignUpForm, UserProfileForm, WorkoutParticipationForm, WorkoutScheduleForm
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta
from django.urls import path
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import TruncMonth, ExtractHour
from django_q.tasks import schedule, async_task
from django.utils.timezone import now
from calendar import month_name
from django.utils.dateformat import format
from django.utils.translation import gettext as _
from django.contrib import messages as django_messages
from .forms import MessageForm
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Message
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Q
from .forms import MessageForm
from .models import User
from django.shortcuts import render, get_object_or_404
from .models import (Plan, PurchaseHistory, ServiceImage, Workout, Coach, Review, WorkoutSchedule, CatalogService, PersonalizedCoaching, GymAccessory, DietPlan)
from django.utils.translation import gettext as _
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from decimal import Decimal
from django.db import transaction
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string
from difflib import get_close_matches
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import WorkoutScheduleForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserProfileForm
from .models import Message 
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Vue pour la bannière de consentement (affichée par défaut)
def cookie_consent_view(request):
    return render(request, "cookie_consent/banner.html")

def cookies_policy(request):
    return render(request, 'path/to/cookies.html')

# Vue pour les préférences de cookies
@csrf_exempt
def cookie_preferences_view(request):
    if request.method == "POST":
        # Traitez et enregistrez les préférences de l'utilisateur
        preferences = request.POST.get('preferences')
        # Enregistrez ou mettez à jour les préférences de l'utilisateur ici selon vos besoins
        return JsonResponse({"status": "preferences saved"})
    return render(request, "cookie_consent/preferences.html")



# Vue pour la page à propos


def about(request):
    return render(request, 'about.html')



def home(request):
    context = {
        'plans': Plan.objects.filter(is_available=True),
        'workouts': Workout.objects.filter(available=True),
        'coachs': Coach.objects.all(),
        'reviews': Review.objects.all(),
        'workoutschedules': WorkoutSchedule.objects.select_related('coach', 'location').all(),
        'message': _("Restez en forme"),
    }
    
    # Charger les services uniques
    context.update(load_services())
    
    
    return render(request, 'home.html', context)



# Fonction de recherche complète

@require_GET
def search(request):
    query = request.GET.get('q', '').strip()
    context = {
        "query": query,
        "results": {
            "workouts": [],
            "coachs": [],
            "plans": [],
            "reviews": [],
            "services": [],
        },
        "url_names": {
            "workouts": "workout_detail",
            "coachs": "coach_detail",
            "plans": "plan_detail",
            "reviews": "review_detail",
            "services": "service_detail",
        },
    }

    if query:
        # Remplissage des résultats en fonction de la requête
        context["results"]["workouts"] = list(Workout.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).values("id", "title", "description"))

        context["results"]["coachs"] = list(Coach.objects.filter(
            Q(username__icontains=query) | Q(about__icontains=query)
        ).values("id", "username", "about"))

        context["results"]["plans"] = list(Plan.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values("id", "name", "description"))

        context["results"]["reviews"] = list(Review.objects.filter(
            Q(content__icontains=query)
        ).values("id", "content"))

        context["results"]["services"] = list(CatalogService.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values("id", "name", "description"))

    if not any(context["results"].values()):
        context["message"] = "Aucun résultat trouvé pour votre recherche."
        context["suggestions"] = get_suggestions(query)
    else:
        context["message"] = None

    # Si la requête est AJAX, retourner un JSON avec le HTML des résultats
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('partials/search_results.html', context, request=request)
        return JsonResponse({"html": html})

    # Sinon, rendre la page de recherche principale
    return render(request, 'searchbar.html', context)

def get_suggestions(query):
    keywords = [
        *Workout.objects.values_list('title', flat=True),
        *Plan.objects.values_list('name', flat=True),
        *CatalogService.objects.values_list('name', flat=True),
        "Conditions de Vente", "Cookies", "À propos", "Mentions Légales", "Confidentialité"
    ]
    return get_close_matches(query, keywords, n=3, cutoff=0.6)

def load_services():
    # Services disponibles
    catalog_services = CatalogService.objects.filter(is_available=True).distinct()
    personalized_coaching = PersonalizedCoaching.objects.select_related('catalog_service', 'coach').all()
    gym_accessories = GymAccessory.objects.select_related('catalog_service').all()
    diet_plans = DietPlan.objects.select_related('catalog_service').all()

    # Initialisation d'un dictionnaire pour éviter les doublons
    all_services_dict = {}

    for service in catalog_services:
        all_services_dict[service.id] = {
            'service': service,
            'type': 'catalog',
            'coach': None,
            'stock': None,
            'partner_company': None,
            'images': ServiceImage.objects.filter(catalog_service=service)
        }

    for coaching in personalized_coaching:
        all_services_dict[coaching.catalog_service.id] = {
            'service': coaching.catalog_service,
            'type': 'personalized_coaching',
            'coach': coaching.coach,
            'stock': None,
            'partner_company': None,
            'images': ServiceImage.objects.filter(catalog_service=coaching.catalog_service)
        }

    for accessory in gym_accessories:
        all_services_dict[accessory.catalog_service.id] = {
            'service': accessory.catalog_service,
            'type': 'gym_accessory',
            'coach': None,
            'stock': accessory.stock,
            'partner_company': None,
            'images': ServiceImage.objects.filter(catalog_service=accessory.catalog_service)
        }

    for diet in diet_plans:
        all_services_dict[diet.catalog_service.id] = {
            'service': diet.catalog_service,
            'type': 'diet_plan',
            'coach': None,
            'stock': None,
            'partner_company': diet.partner_company,
            'images': ServiceImage.objects.filter(catalog_service=diet.catalog_service)
        }

    # Convertir le dictionnaire en liste pour le template
    all_services = list(all_services_dict.values())

    return {'all_services': all_services}



def load_single_service(catalog_service_id):
    # Récupérer le service principal
    catalog_service = get_object_or_404(CatalogService, id=catalog_service_id)

    # Récupérer les objets ServiceImage directement pour garder les instances complètes
    images = ServiceImage.objects.filter(catalog_service=catalog_service)

    # Initialisation du dictionnaire de données pour le service
    service_data = {
        'service': catalog_service,
        'images': images,  # On passe les objets complets
        'type': 'catalog',
        'coach': None,
        'stock': None,
        'partner_company': None
    }

    # Détecter le type de service et charger les attributs spécifiques en utilisant try-except
    try:
        diet_plan = DietPlan.objects.get(catalog_service=catalog_service)
        service_data.update({
            'type': 'diet_plan',
            'partner_company': diet_plan.partner_company,
        })
    except DietPlan.DoesNotExist:
        try:
            gym_accessory = GymAccessory.objects.get(catalog_service=catalog_service)
            service_data.update({
                'type': 'gym_accessory',
                'stock': gym_accessory.stock,
            })
        except GymAccessory.DoesNotExist:
            try:
                personalized_coaching = PersonalizedCoaching.objects.get(catalog_service=catalog_service)
                service_data.update({
                    'type': 'personalized_coaching',
                    'coach': personalized_coaching.coach,
                })
            except PersonalizedCoaching.DoesNotExist:
                pass

    return service_data


def service_detail(request, catalog_service_id):
    service_data = load_single_service(catalog_service_id)
    print("Service Data:", service_data)  # Debug: Afficher les données dans la console
    return render(request, 'service_detail.html', {'service_data': service_data})


# Vue pour la page FAQ


def faq(request):
    return render(request, 'faq.html')




# Notification pour relancer abonnement arriver a echeance
@login_required
def remind_subscription(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        Subscription = get_object_or_404(Subscription, user=user, payment_status='pending')

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
            messages.success(request, f'Bienvenue 😊, {user.username}!')
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

# Message envoye en auto des qu un user change de mot de passe , il est sauveagarder avec le signal pre save et post save voir le fichier signal.py
@receiver(post_save, sender=User)
def send_password_change_notification(sender, instance, created, **kwargs):
    # Vérifier si c'est une modification et pas une création
    if not created:
        # Comparer le mot de passe avant et après pour détecter un changement
        if instance.password != instance.__original_password:
            try:
                # Récupérer un administrateur (ou un utilisateur staff) pour envoyer le message
                admin_user = User.objects.filter(is_staff=True).first()

                if admin_user:
                    # Créer le message de confirmation uniquement pour un changement de mot de passe
                    Message.objects.create(
                        sender=admin_user,  # L'administrateur est l'expéditeur
                        recipient=instance,  # L'utilisateur qui a changé son mot de passe
                        subject="Modification de votre mot de passe",
                        body="Votre mot de passe a été modifié avec succès. Si vous n'êtes pas à l'origine de ce changement, veuillez contacter l'administrateur."
                    )
                    print(f"Message de confirmation envoyé à {instance.username}.")
                else:
                    print("[Erreur] Aucun utilisateur administrateur trouvé pour envoyer le message.")

            except Exception as e:
                print(f"Erreur lors de l'envoi du message de changement de mot de passe : {e}")







@login_required
def read_message(request, message_id):
    # Récupérer le message spécifique en utilisant Q pour vérifier l'expéditeur ou le destinataire
    message = get_object_or_404(
        Message,
        Q(sender=request.user) | Q(recipient=request.user),
        id=message_id
    )

    # Marquer le message comme lu
    if not message.is_read:
        message.is_read = True
        message.save()

    # Récupérer tous les messages de la discussion entre l'utilisateur et l'expéditeur
    thread_messages = Message.objects.filter(
        Q(sender=message.sender, recipient=request.user) |
        Q(sender=request.user, recipient=message.sender)
    ).order_by('timestamp')

    # Récupérer un destinataire valide pour "Nouveau message"
    recipient = User.objects.exclude(id=request.user.id).first()

    # Compteur pour les messages importants et archivés
    important_messages_count = Message.objects.filter(recipient=request.user, is_important=True).count()
    archived_messages_count = Message.objects.filter(recipient=request.user, is_archived=True).count()

    context = {
        'message': message,
        'recipient': recipient,
        'thread_messages': thread_messages,
        'important_messages_count': important_messages_count,
        'archived_messages_count': archived_messages_count,
    }

    return render(request, 'read_message.html', context)


@login_required
def archive_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender == request.user or message.recipient == request.user:
        message.is_archived = not message.is_archived  # Basculer l'état d'archivage
        message.save()
        return JsonResponse({'success': True, 'is_archived': message.is_archived})
    return HttpResponseForbidden("Vous n'avez pas l'autorisation d'archiver ce message.")

@login_required
def mark_important(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender == request.user or message.recipient == request.user:
        message.is_important = not message.is_important  # Basculer l'état important
        message.save()
        return JsonResponse({'success': True, 'is_important': message.is_important})
    return HttpResponseForbidden("Vous n'avez pas l'autorisation de marquer ce message comme important.")



@login_required
def drafts(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject = data.get('subject')
        body = data.get('body')
        recipient_id = data.get('recipient_id')

        # Créer ou mettre à jour un brouillon
        draft, created = Message.objects.update_or_create(
            sender=request.user,
            recipient_id=recipient_id,
            defaults={
                'subject': subject,
                'body': body,
                'is_draft': True
            }
        )

        return JsonResponse({'success': True})

    # Récupérer tous les brouillons pour l'utilisateur connecté
    drafts = Message.objects.filter(sender=request.user, is_draft=True).order_by('-timestamp')

    context = {
        'drafts': drafts
    }

    return render(request, 'drafts.html', context)

@login_required
def delete_draft(request, draft_id):
    draft = get_object_or_404(Message, id=draft_id, sender=request.user, is_draft=True)
    draft.delete()
    return redirect('drafts')  # Redirige vers la page des brouillons


def restore_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    if message.is_deleted:
        message.is_deleted = False  # Supposons que tu utilises un champ `is_deleted` pour la corbeille
        message.save()
        messages.success(request, "Le message a été restauré avec succès.")
    else:
        messages.error(request, "Le message n'est pas dans la corbeille.")
    
    return redirect('messages_inbox')


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)

    # Marquer le message comme supprimé au lieu de le supprimer définitivement
    message.is_deleted = True
    message.save()

    return redirect('messages_inbox')



@login_required
def delete_multiple_messages(request):
    if request.method == 'POST':
        # Récupérer la liste des messages sélectionnés
        message_ids = request.POST.getlist('selected_messages')

        # Supprimer les messages correspondant aux IDs récupérés
        for message_id in message_ids:
            try:
                message = Message.objects.get(id=message_id, recipient=request.user)
                # Marquer le message comme supprimé au lieu de le supprimer définitivement
                message.is_deleted = True
                message.save()  # Enregistrer le changement dans la base de données
            except Message.DoesNotExist:
                pass  # Si le message n'existe pas, ignorer l'erreur

    # Rediriger vers la boîte de réception après suppression
    return redirect('messages_inbox')


def messages_inbox(request):
    # Récupérer la catégorie depuis l'URL
    category = request.GET.get('category', 'received')
    filter_role = request.GET.get('filter_role', 'all')

    # Filtrer les messages en fonction de la catégorie sélectionnée
    if category == 'received':
        messages = Message.objects.filter(recipient=request.user, is_deleted=False).order_by('-timestamp')  # Tri par date descendante
    elif category == 'sent':
        messages = Message.objects.filter(sender=request.user).order_by('-timestamp')  # Tri par date descendante
    elif category == 'drafts':
        messages = Message.objects.filter(sender=request.user, is_draft=True).order_by('-timestamp')  # Tri par date descendante
    elif category == 'important':
        messages = Message.objects.filter(recipient=request.user, is_important=True).order_by('-timestamp')  # Tri par date descendante
    elif category == 'trash':
        messages = Message.objects.filter(recipient=request.user, is_deleted=True).order_by('-timestamp')  # Tri par date descendante
    elif category == 'archived':
        messages = Message.objects.filter(recipient=request.user, is_archived=True).order_by('-timestamp')  # Tri par date descendante
    elif category == 'unread':
        messages = Message.objects.filter(recipient=request.user, is_read=False, is_deleted=False).order_by('-timestamp')  # Tri par date descendante
    else:
        messages = Message.objects.filter(recipient=request.user, is_deleted=False).order_by('-timestamp')  # Tri par date descendante

    # Appliquer les filtres de rôle
    if filter_role == 'all':
        messages = messages
    elif filter_role == 'user':
        messages = messages.filter(sender__role='user')
    elif filter_role == 'coach':
        messages = messages.filter(sender__role='coach')
    elif filter_role == 'staff':
        messages = messages.filter(sender__is_staff=True)

    # Compter les messages dans chaque catégorie
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False, is_deleted=False).count()
    draft_messages_count = Message.objects.filter(sender=request.user, is_draft=True).count()
    sent_messages_count = Message.objects.filter(sender=request.user).count()
    trash_messages_count = Message.objects.filter(recipient=request.user, is_deleted=True).count()
    important_messages_count = Message.objects.filter(recipient=request.user, is_important=True).count()
    archived_messages_count = Message.objects.filter(recipient=request.user, is_archived=True).count()
    total_messages_count = Message.objects.filter(recipient=request.user, is_deleted=False).count()

    context = {
        'messages': messages,
        'category': category,
        'filter_role': filter_role,
        'unread_messages': unread_messages,
        'draft_messages_count': draft_messages_count,
        'sent_messages_count': sent_messages_count,
        'trash_messages_count': trash_messages_count,
        'important_messages_count': important_messages_count,
        'archived_messages_count': archived_messages_count,
        'total_messages_count': total_messages_count,
    }

    return render(request, 'messages_inbox.html', context)


@login_required
def send_message(request, recipient_id=None):
    # Initialiser recipient à None pour les nouveaux messages
    recipient = None

    # Gestion des utilisateurs en fonction du rôle
    if request.user.role == 'member':
        users = User.objects.filter(Q(role='coach') | Q(is_staff=True)).exclude(id=request.user.id)
    elif request.user.role == 'coach':
        users = User.objects.filter(Q(role='member') | Q(role='coach') | Q(is_staff=True)).exclude(id=request.user.id)
    elif request.user.is_staff:
        users = User.objects.all().exclude(id=request.user.id)

    # Si recipient_id est présent, c'est une réponse à un message
    if recipient_id:
        recipient = get_object_or_404(User, id=recipient_id)

    subject = request.GET.get('subject', '')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Récupérer l'ID du destinataire depuis le formulaire
            recipient_id = request.POST.get('recipient')
            recipient = get_object_or_404(User, id=recipient_id)

            # Créer et sauvegarder le message
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()

            messages.success(request, "Message envoyé avec succès.")
            return redirect('messages_inbox')
    else:
        # Si c'est un nouveau message, ne pré-remplir aucune donnée
        initial_data = {'subject': f"RE: {subject}" if recipient else ''}
        if recipient:
            initial_data['recipient'] = recipient.id  # Pour une réponse, pré-remplir

        form = MessageForm(initial=initial_data)

    return render(request, 'send_message.html', {
        'form': form,
        'users': users,
        'subject': subject,
        'recipient': recipient  # Transmettre seulement pour les réponses
    })




# Contact d'un coach
@login_required
def contact_coach(request, coach_id):
    coach = get_object_or_404(User, id=coach_id)
    if request.method == 'POST':
        message_body = request.POST.get('message')
        Message.objects.create(
            sender=request.user,
            recipient=coach,
            subject=f"Nouveau message de {request.user.get_full_name()}",
            body=message_body,
            is_read=False  # Le message est créé avec un statut "non lu"
        )
        django_messages.success(request, f"Message envoyé à {coach.get_full_name()}")
        return redirect('coach_dashboard')
    return HttpResponseForbidden("Action non autorisée")

# Contact d'un membre
@login_required
def contact_member(request, member_id):
    member = get_object_or_404(User, id=member_id)
    if request.method == 'POST':
        message_body = request.POST.get('message')
        Message.objects.create(
            sender=request.user,
            recipient=member,
            subject=f"Message de {request.user.get_full_name()}",
            body=message_body,
            is_read=False  # Message non lu à la création
        )
        django_messages.success(request, f"Message envoyé à {member.get_full_name()}")
        return redirect('admin_dashboard')
    return HttpResponseForbidden("Méthode non autorisée")



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
    
    # Récupérer le staff (si disponible) uniquement si le rôle est 'member'
    staff_id = None
    if user.role == 'member':
        staff_user = User.objects.filter(is_staff=True).first()
        staff_id = staff_user.id if staff_user else None

    # Récupérer l'abonnement actuel en vérifiant le statut et le plan associé
    current_subscription = Subscription.objects.filter(
        user=user,
        payment_status='paid'
    ).select_related('plan').first()

    # Si l'utilisateur n'a pas de souscription active, afficher le popup
    show_subscription_popup = (
        current_subscription is None or 
        (current_subscription.get_end_date() and current_subscription.get_end_date() < timezone.now().date())
    )

    # Récupérer l'historique des achats (plans et services)
    purchase_history = PurchaseHistory.objects.filter(user=user).select_related('plan', 'catalog_service').order_by('-purchase_date')
    
    # Filtrer les achats en deux catégories : plans et services
    plan_purchases = purchase_history.filter(item_type='plan')
    service_purchases = purchase_history.filter(item_type='service')

    # Préparer les données pour le template
    context = {
        'user': user,  
        'staff_id': staff_id,
        'current_subscription': current_subscription,
        'is_premium': user.is_premium, 
        'show_subscription_popup': show_subscription_popup,
        'purchase_history': purchase_history,  # Historique global des achats si besoin
        'plan_purchases': plan_purchases,       # Achats de plans
        'service_purchases': service_purchases, # Achats de services
    }

    return render(request, 'profile.html', context)





# def migrate_old_purchases():
#     users = User.objects.all()
    
#     with transaction.atomic():
#         for user in users:
#             # Récupérer les abonnements payés
#             old_subscriptions = Subscription.objects.filter(user=user, payment_status='paid')
#             for subscription in old_subscriptions:
#                 PurchaseHistory.objects.create(
#                     user=user,
#                     item_type='plan',
#                     price=subscription.plan.price,
#                     purchase_date=subscription.start_date,  # Utiliser le champ existant représentant la date d'achat
#                     plan=subscription.plan
#                 )
#                 print(f"Ajout de l'abonnement pour {user.username}")

#             # Suppression de la tentative d'ajout des CatalogService sans champ user
#             print(f"Migration terminée pour {user.username}")

# # Appeler la fonction pour effectuer la migration
# migrate_old_purchases()


def download_invoice(request, purchase_id):
    # Récupérer l'achat et l'utilisateur
    purchase = get_object_or_404(PurchaseHistory, id=purchase_id, user=request.user)
    user = request.user

    # Préparer la réponse pour un PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{purchase.id}.pdf"'

    # Créer un PDF avec reportlab
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Coordonnées de BE Fit en haut à droite
    p.setFont("Helvetica", 10)
    p.drawString(width - 200, height - 50, "BE Fit")
    p.drawString(width - 200, height - 65, "Adresse : 18, Place Eugene Simonis")
    p.drawString(width - 200, height - 80, "Ville : Bruxelles, BE 1081")
    p.drawString(width - 200, height - 95, "Tél. : +32 484 86 01 33")
    p.drawString(width - 200, height - 110, "Email : befit@gmail.com")
    p.drawString(width - 200, height - 125, "Horaires : Du Lu au Dim de 07h à 19h")

    # Coordonnées de l'utilisateur en haut à gauche
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 50, "Adresse de livraison")
    p.drawString(50, height - 65, f"Nom: {user.first_name} {user.last_name}")
    p.drawString(50, height - 80, f"Email: {user.email}")
    p.drawString(50, height - 95, f"Adresse: {user.address or 'Non renseignée'}")

    # Date et numéro de facture
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 130, f"Date de la facture : {datetime.now().strftime('%d %m %Y')}")
    p.drawString(50, height - 145, f"Numéro de facture : {purchase.id}-{datetime.now().strftime('%Y%m%d')}")

    # Titre de la facture
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 170, "Facture d'achat")

    # Période de l'achat basée sur la date d'achat
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 190, f"Période : {purchase.purchase_date.strftime('%B %Y')}")

    # Détail de l'achat
    y_position = height - 220
    price_tvac = Decimal(purchase.price)
    price_htva = price_tvac / Decimal("1.21")
    tva_amount = price_tvac - price_htva

    # Affichage du détail de l'achat
    p.setFont("Helvetica", 10)
    p.drawString(50, y_position, f"{purchase.get_item_name()} - {price_htva.quantize(Decimal('0.01'))}€ HTVA - {tva_amount.quantize(Decimal('0.01'))}€ TVA - {price_tvac}€ TVAC")
    y_position -= 15
    if purchase.item_type == 'plan':
        p.drawString(60, y_position, f"Durée: {purchase.get_duration()} jours")
        y_position -= 15
        p.drawString(60, y_position, f"Date d'échéance: {purchase.get_end_date().strftime('%d %m %Y') if purchase.get_end_date() else 'Non renseignée'}")
        y_position -= 15

    # Totaux HTVA et TVAC pour cet achat unique
    total_htva = price_htva
    total_tva = tva_amount
    total_tvac = price_tvac

    # Affichage des totaux
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, f"Total HTVA : {total_htva.quantize(Decimal('0.01'))}€")
    y_position -= 15
    p.drawString(50, y_position, f"Total TVA (21%) : {total_tva.quantize(Decimal('0.01'))}€")
    y_position -= 15
    p.drawString(50, y_position, f"Total TVAC : {total_tvac.quantize(Decimal('0.01'))}€")

    # Clauses légales
    y_position -= 50
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_position, "Politique de rétractation :")
    p.setFont("Helvetica", 8)
    p.drawString(50, y_position - 12, "Conformément à l'article VI.47 du Code de droit économique, les consommateurs ont un droit de rétractation de 14 jours pour les services non entamés.")
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_position, "Garantie légale :")
    p.setFont("Helvetica", 8)
    p.drawString(50, y_position - 12, "Les produits bénéficient d'une garantie légale de 2 ans selon l'article 1649bis du Code civil belge.")

    y_position -= 40
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_position, "Confidentialité :")
    p.setFont("Helvetica", 8)
    p.drawString(50, y_position - 12, "Les informations personnelles sont protégées selon notre politique de confidentialité.")

    # Sauvegarder et fermer le PDF
    p.showPage()
    p.save()

    return response




# def remove_duplicates():
#     duplicates = (
#         PurchaseHistory.objects
#         .values('user', 'item_type', 'plan', 'catalog_service')
#         .annotate(count=Count('id'))
#         .filter(count__gt=1)
#     )

#     with transaction.atomic():
#         for duplicate in duplicates:
#             entries = PurchaseHistory.objects.filter(
#                 user=duplicate['user'],
#                 item_type=duplicate['item_type'],
#                 plan=duplicate['plan'],
#                 catalog_service=duplicate['catalog_service']
#             ).order_by('id')
            
#             entries_to_delete = entries[1:]  # Garder le premier et supprimer les autres
#             print(f"Suppression des doublons pour {duplicate} - Total à supprimer : {len(entries_to_delete)}")
#             entries_to_delete.delete()

#     print("Suppression des doublons terminée.")








    


    # Récupérer les séances passées avec ce coach (si l'utilisateur est un coach ou admin)
    # if user.is_staff or user.role == 'coach':
    #     member_sessions = WorkoutSchedule.objects.filter(coach=user).prefetch_related('participants')
    #     total_sessions = member_sessions.count()
    #     members_with_sessions = member_sessions.values('participants__first_name', 'participants__last_name', 'participants__email', 'participants__is_premium').distinct()
    # else:
    #     total_sessions = 0
    #     members_with_sessions = None

   




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
    return render(request, 'home_dashboard.html', {
        'stats': stats,
        'members': members,
        'subscriptions': subscriptions,
        'coaches': coaches,
        'total_sessions':  total_sessions,
        'members_with_sessions': members_with_sessions,
    })




from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import WorkoutScheduleForm
from .models import WorkoutSchedule, User, Workout
from django.utils import timezone

@login_required
@user_passes_test(lambda u: u.role in ['coach', 'admin'])
def add_workout_schedule(request):
    user = request.user

    # Récupération de tous les créneaux sans filtre par rôle
    schedule_queryset = WorkoutSchedule.objects.all()

    # Récupération des utilisateurs pouvant être ajoutés en tant que participants
    participants_queryset = User.objects.filter(role='member').only('first_name', 'last_name', 'email')

    # Filtrer les workouts selon les spécialités du coach
    if user.role == 'coach':
        try:
            # Accède aux spécialités du coach à travers la relation OneToOne avec User
            workout_queryset = user.coach.specialties.all()
        except Coach.DoesNotExist:
            # Gestion de l'erreur si le coach n'existe pas pour cet utilisateur
            workout_queryset = Workout.objects.none()
    else:
        workout_queryset = Workout.objects.all()

    if request.method == 'POST':
        form = WorkoutScheduleForm(request.POST, user=user, schedule=schedule_queryset, workout_queryset=workout_queryset)
        
        if form.is_valid():
            workout_schedule = form.save(commit=False)
            workout_schedule.coach = user
            workout_schedule.save()
            form.save_m2m()  # Sauvegarde des relations ManyToMany (participants)
            messages.success(request, "Séance de workout créée avec succès.")
            return redirect('coach_dashboard' if user.role == 'coach' else 'admin_dashboard')
        else:
            messages.error(request, "Erreur dans le formulaire. Veuillez vérifier les champs.")
    else:
        form = WorkoutScheduleForm(user=user, schedule=schedule_queryset, workout_queryset=workout_queryset)

    return render(request, 'newWorkoutSchedule.html', {
        'form': form,
        'participants': participants_queryset,
    })

def get_schedule_details(request, schedule_id):
    try:
        schedule = WorkoutSchedule.objects.get(id=schedule_id)
        data = {
            'start_time': schedule.start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': schedule.end_time.strftime('%Y-%m-%dT%H:%M')
        }
        return JsonResponse(data)
    except WorkoutSchedule.DoesNotExist:
        return JsonResponse({'error': 'Créneau non trouvé'}, status=404)



@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")

    # Récupérer l'année et le mois depuis l'URL
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')

    # Utiliser le mois actuel si aucun mois n'est sélectionné
    if not selected_year or not selected_month:
        now = timezone.now()
        selected_year = now.year
        selected_month = now.month
    else:
        selected_year = int(selected_year)
        selected_month = int(selected_month)

    # Bloquer la navigation dans le futur
    now = timezone.now()
    if selected_year > now.year or (selected_year == now.year and selected_month > now.month):
        return render(request, 'admin_dashboard.html', {
            'message': "Aucune donnée disponible pour ce mois.",
            'current_year': now.year,
            'current_month': now.month,
        })

    # Récupérer les coachs, membres et abonnements
    coaches = Coach.objects.select_related('user').order_by('-user__date_joined')
    members = User.objects.filter(is_staff=False).order_by('-date_joined')
    subscriptions = Subscription.objects.select_related('user', 'plan').order_by('-start_date')

    # Statistiques des séances, calcul des pourcentages
    schedules = WorkoutSchedule.objects.filter(start_time__month=selected_month, start_time__year=selected_year)
    total_participants = 0
    total_present = 0
    stats = []
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

    # Calcul du taux d'inscription
    total_members = members.count()
    monthly_new_members = members.filter(date_joined__year=selected_year, date_joined__month=selected_month).count()
    if total_members > 0:
        monthly_registration_percentage = (monthly_new_members / total_members) * 100
    else:
        monthly_registration_percentage = 0

    # Calcul du taux de participation
    if total_participants > 0:
        attendance_percentage = (total_present / total_participants) * 100
    else:
        attendance_percentage = 0

    # Calcul des heures les plus fréquentées
    busy_hour_counts = {}
    for hour in range(7, 19):
        busy_hour_counts[hour] = schedules.filter(start_time__hour=hour).count()

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
    if schedules.count() > 0:
        for workout in workout_frequencies:
            workout_percentages.append({
                'workout_title': workout['workout__title'],
                'percentage': (workout['count'] / schedules.count()) * 100
            })

    # Calcul du taux de séances par coach
    coach_schedule_counts = schedules.values('coach__first_name', 'coach__last_name').annotate(count=Count('coach')).order_by('-count')
    coach_percentages = []
    if schedules.count() > 0:
        for coach in coach_schedule_counts:
            coach_percentages.append({
                'coach_name': f"{coach['coach__first_name']} {coach['coach__last_name']}",
                'percentage': (coach['count'] / schedules.count()) * 100
            })

    # Calculer les mois précédent et suivant
    def get_previous_month(year, month):
        if month == 1:
            return (year - 1, 12)
        else:
            return (year, month - 1)

    def get_next_month(year, month):
        if month == 12:
            return (year + 1, 1)
        else:
            return (year, month + 1)

    previous_year, previous_month = get_previous_month(selected_year, selected_month)
    next_year, next_month = get_next_month(selected_year, selected_month)

    # Bloquer le mois futur
    no_next_data = next_year > now.year or (next_year == now.year and next_month > now.month)

    context = {
        'coaches': coaches,
        'members': members,
        'subscriptions': subscriptions,
        'attendance_percentage': attendance_percentage,
        'monthly_registration_percentage': monthly_registration_percentage,
        'plan_percentages': plan_percentages,
        'workout_percentages': workout_percentages,
        'coach_percentages': coach_percentages,
        'busy_hour_counts_keys': list(busy_hour_counts.keys()),
        'busy_hour_counts_values': list(busy_hour_counts.values()),
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_month_name': month_name[selected_month],  # Nom du mois
        'current_year': now.year,
        'current_month': now.month,
        'previous_year': previous_year,
        'previous_month': previous_month,
        'next_year': next_year,
        'next_month': next_month,
        'no_next_data': no_next_data,
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


# N est pas utiliser actuellement car idem que politique de confidentialite
def mentions_legales(request):
    return render(request, 'mentions_legales.html')
