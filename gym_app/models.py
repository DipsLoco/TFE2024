from datetime import datetime, time, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

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
    image = models.ImageField(upload_to='membre_images/', blank=True, null=True)  # Image du membre
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)  # Nom unique pour éviter les conflits
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)  # Nom unique pour éviter les conflits


class Location(models.Model):
    name = models.CharField(max_length=100)  # Nom de la location
    address = models.CharField(max_length=255)  # Adresse
    city = models.CharField(max_length=100)  # Ville
    state = models.BooleanField()  # Statut (location active ou non ?)
    postal_code = models.IntegerField()  # Code postal

    def __str__(self):
        return self.name


class Workout(models.Model):
    title = models.CharField(max_length=200)  # Titre de la séance
    description = models.TextField()  # Description de la séance
    duration = models.DurationField()  # Durée de la séance
    available = models.BooleanField(default=True)  # Disponibilité de la séance
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  # Localisation de la séance
    coachs = models.ManyToManyField('Coach', related_name='workouts')  # Coachs associés à la séance

    def __str__(self):
        return self.title

    def get_main_image(self):
        return self.images.first()  # Retourne la première image associée à ce Workout


class WorkoutImage(models.Model):
    workout = models.ForeignKey(Workout, related_name='images', on_delete=models.CASCADE)  # Séance associée
    image = models.ImageField(upload_to='workout_images/')  # Image de la séance
    description = models.CharField(max_length=255, blank=True, null=True)  # Description de l'image

    def __str__(self):
        return self.description if self.description else f'Image for {self.workout.title}'


class WorkoutSchedule(models.Model):
    workout = models.ForeignKey('Workout', on_delete=models.CASCADE)  # Séance associée
    start_time = models.DateTimeField()  # Heure de début de la séance
    end_time = models.DateTimeField()  # Heure de fin de la séance
    location = models.ForeignKey('Location', on_delete=models.CASCADE)  # Lieu de la séance
    coach = models.ForeignKey('User', on_delete=models.CASCADE, related_name='scheduled_workouts')  # Coach de la séance
    participants = models.ManyToManyField('User', related_name='workout_participants')  # Participants à la séance
    available = models.BooleanField(default=True)  # Disponibilité de la réservation
    expired = models.BooleanField(default=False)  # Séance expirée par défaut à False
    complet = models.BooleanField(default=False)  # Séance complète ou non

    def __str__(self):
        if self.start_time:
            return f"{self.workout.title} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
        return f"{self.workout.title} - (heure non définie)"

    def clean(self):
        # Rendre start_time et end_time "aware" si elles sont "naive"
        if self.start_time and timezone.is_naive(self.start_time):
            self.start_time = timezone.make_aware(self.start_time)

        if self.end_time and timezone.is_naive(self.end_time):
            self.end_time = timezone.make_aware(self.end_time)

        # Validation pour limiter le nombre de participants
        if self.pk and self.participants.count() > 10:
            raise ValidationError('Vous ne pouvez pas ajouter plus de 10 participants à une séance.')

        # Validation pour s'assurer que l'heure de fin est après l'heure de début
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('L\'heure de début doit être avant l\'heure de fin.')

    def save(self, *args, **kwargs):
        # Validation avant la sauvegarde
        self.clean()

        # Sauvegarde initiale de l'objet
        super().save(*args, **kwargs)

        # Mettre à jour la disponibilité après la sauvegarde
        self.update_complet()

    def update_complet(self):
        # Met à jour l'attribut 'complet' et 'available' en fonction du nombre de participants
        if self.participants.count() >= 10:
            self.complet = True
            self.available = False  # Si la séance est complète, elle n'est plus disponible
        else:
            self.complet = False
            self.available = True  # Si la séance n'est pas complète, elle reste disponible
        super().save(update_fields=['complet', 'available'])  # Sauvegarder uniquement les champs 'complet' et 'available'

    def update_expired_status(self):
        # Mise à jour du statut 'expired' en fonction de l'heure actuelle
        if not self.expired and self.start_time:
            if timezone.is_naive(self.start_time):
                self.start_time = timezone.make_aware(self.start_time)

            # Comparer avec l'heure actuelle pour déterminer si la séance est expirée
            if self.start_time < timezone.now():
                self.expired = True
                super().save(update_fields=['expired'])  # Sauvegarder uniquement le champ 'expired'

    @staticmethod
    def create_default_schedules(workout, location, coach):
        # Crée des séances par défaut pour une semaine avec des créneaux horaires fixes
        time_slots = [
            (8, 10),
            (10, 12),
            (14, 16),
            (16, 18),
        ]
        for day_offset in range(6):  # Pour les 6 premiers jours de la semaine
            date = timezone.now().date() + timedelta(days=day_offset)
            for start_hour, end_hour in time_slots:
                start_time = timezone.make_aware(datetime.combine(date, time(start_hour)))
                end_time = timezone.make_aware(datetime.combine(date, time(end_hour)))
                WorkoutSchedule.objects.create(
                    workout=workout,
                    start_time=start_time,
                    end_time=end_time,
                    location=location,
                    coach=coach,
                )

# Enregistrer le signal après la définition complète du modèle
@receiver(m2m_changed, sender=WorkoutSchedule.participants.through)
def update_complet_status(sender, instance, **kwargs):
    # Met à jour l'attribut 'complet' et 'available' chaque fois que les participants changent
    instance.update_complet()

# Signal pour mettre à jour le statut 'expired' après chaque sauvegarde
@receiver(post_save, sender=WorkoutSchedule)
def check_expired_status(sender, instance, **kwargs):
    instance.update_expired_status()

class WorkoutParticipation(models.Model):
    workout_schedule = models.ForeignKey('WorkoutSchedule', on_delete=models.CASCADE)  # Référence à la séance
    participant = models.ForeignKey(User, on_delete=models.CASCADE)  # Référence à l'utilisateur/participant
    present = models.BooleanField(default=False)  # Présence validée ou non par le coach

    class Meta:
        unique_together = ['workout_schedule', 'participant']  # Empêche la duplication des participations

    def __str__(self):
        return f"{self.participant.username} - {self.workout_schedule.workout.title} - Présent: {self.present}"





class Coach(models.Model):
    username = models.CharField(max_length=50, unique=True)  # Nom d'utilisateur du coach
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ID de l'utilisateur
    specialties = models.ManyToManyField(Workout, related_name='specialties')  # Spécialités du coach
    available = models.BooleanField(default=False)  # Disponibilités du coach
    image = models.ImageField(upload_to='coach_images/', blank=True, null=True)  # Image du coach
    exp = models.PositiveIntegerField(default=0)  # Expérience du coach en années

    def __str__(self):
        return self.username


class Plan(models.Model):
    name = models.CharField(max_length=100)  # Nom du plan
    description = models.TextField()  # Description du plan
    price = models.IntegerField()  # Prix du plan
    duration = models.IntegerField()  # Durée du plan en jours
    image = models.ImageField(upload_to='plan_images/', blank=True, null=True)  # Image du plan
    is_available = models.BooleanField(default=False)  # Disponibilité du plan
    is_premium = models.BooleanField(default=False)  # Si l user a pris un plan alors vip sinon pas vip



class Subscription(models.Model):  # Statut abonnement
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'En ordre de paiement'),
        ('refused', 'Paiement refusé'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ID de l'utilisateur
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)  # ID du plan
    start_date = models.DateField(auto_now_add=True)  # Date de début de l'abonnement
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')  # Statut du paiement

    def get_end_date(self):
        return self.start_date + timedelta(days=self.plan.duration)

    def save(self, *args, **kwargs):
        if self.payment_status == 'paid':
            self.user.is_premium = True
            self.user.save()
        super().save(*args, **kwargs)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ID de l'utilisateur
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)  # ID de la séance
    content = models.TextField()  # Contenu du commentaire utilisateur
    datetime = models.DateTimeField(default=timezone.now)  # Date et heure du commentaire

