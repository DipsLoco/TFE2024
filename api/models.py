from datetime import timedelta, timezone
from django.db import models
from gym_app import models
from datetime import datetime, time, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.auth import get_user_model
from django_q.tasks import async_task

# api/models.py

from gym_app.models import User, Plan, Coach, Subscription, PurchaseHistory, Workout, Review, WorkoutParticipation, WorkoutSchedule
from django.contrib.auth import get_user_model
User = get_user_model()

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('coach', 'Coach'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')  # Rôle de l'utilisateur
    last_name = models.CharField(max_length=100)  # Nom de famille de l'utilisateur
    first_name = models.CharField(max_length=100)  # Prénom de l'utilisateur
    birth_date = models.DateField(default=timezone.now)  # Date de naissance
    email = models.EmailField()  # Adresse email
    phone = models.CharField(max_length=15)  # Numéro de téléphone
    address = models.CharField(max_length=255)  # Adresse postale
    postal_code = models.IntegerField(default=1000)  # Code postal
    is_premium = models.BooleanField(default=False)  # Statut premium
    date_joined = models.DateTimeField(default=timezone.now)  # Date de création du compte
    social_url = models.URLField(blank=True, null=True)  # URL des réseaux sociaux
    instagram_url = models.URLField(blank=True, null=True)  # URL d'Instagram de l'utilisateur
    image = models.ImageField(upload_to='membre_images/', blank=True, null=True)  # Image du membre

    groups = models.ManyToManyField(Group, related_name='api_app_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='api_app_user_permissions', blank=True)



    
    # Project futur Récupérer les absences des 30 derniers jours
    def recent_absences(self):
        recent_participations = WorkoutParticipation.objects.filter(
            participant=self,
            present=False,
            workout_schedule__start_time__gte=timezone.now() - timedelta(days=30)
        )
        return recent_participations.count()
