from datetime import datetime, timedelta, time
from django.utils import timezone
from django.contrib import admin
from django import forms
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import User, Workout, Coach, Location, Plan, Subscription, Review, WorkoutImage, WorkoutSchedule

# Gestion des utilisateurs avec la possibilité d'ajouter des spécialités pour les coachs
class CoachInline(admin.StackedInline):
    model = Coach
    can_delete = False
    verbose_name_plural = 'Coach'
    filter_horizontal = ['specialties']

class CustomUserAdmin(admin.ModelAdmin):
    inlines = [CoachInline]
    list_display = ['id', 'username', 'role', 'last_name', 'first_name', 'birth_date', 'email', 'phone', 'address', 'postal_code', 'is_premium', 'social_url', 'date_joined']
    list_filter = ['role', 'is_premium']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Gestion des workouts et de leurs images
class WorkoutAdminForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les coachs basés sur les spécialités du workout
        if self.instance.pk:
            self.fields['coachs'].queryset = self.instance.specialties.all()

class WorkoutImageInline(admin.TabularInline):
    model = WorkoutImage
    extra = 1

class WorkoutAdmin(admin.ModelAdmin):
    form = WorkoutAdminForm
    list_display = ['id', 'title', 'description', 'duration', 'available', 'created_at', 'location']
    list_filter = ['available', 'location']
    search_fields = ['title', 'description']
    filter_horizontal = ['coachs']
    inlines = [WorkoutImageInline]

    def save_model(self, request, obj, form, change):
        # Enregistrer l'objet Workout pour obtenir un ID valide
        super().save_model(request, obj, form, change)

# Fonction pour créer les créneaux horaires par défaut pour un Workout donné
def create_default_workout_schedules(workout):
    pass  # Désactivation de la création automatique de créneaux

# Signal pour créer les créneaux après que les coachs ont été assignés
@receiver(m2m_changed, sender=Workout.coachs.through)
def create_schedules_after_coachs_assigned(sender, instance, action, **kwargs):
    if action == "post_add":  # Une fois que la relation many-to-many est mise à jour
        pass  # Désactivation de la création automatique de créneaux

class WorkoutScheduleForm(forms.ModelForm):
    TIME_SLOTS = [
        ('08:00:00', '08:00 - 10:00'),
        ('10:00:00', '10:00 - 12:00'),
        ('14:00:00', '14:00 - 16:00'),
        ('16:00:00', '16:00 - 18:00'),
    ]

    # Création du champ de choix pour les créneaux horaires
    time_slot = forms.ChoiceField(choices=TIME_SLOTS, label="Sélectionnez un créneau horaire")
    date = forms.DateField(label="Date de la séance", widget=forms.SelectDateWidget, initial=timezone.now)  # Date par défaut aujourd'hui

    class Meta:
        model = WorkoutSchedule
        fields = ['workout', 'location', 'coach', 'start_time','date', 'time_slot']  # Limite les champs affichés à 'date' et 'time_slot'

    def save(self, commit=True):
        time_slot = self.cleaned_data['time_slot']  # Récupère le créneau sélectionné
        date = self.cleaned_data['date']  # Date sélectionnée

        # Transformation du créneau en heures
        start_hour, start_minute, _ = map(int, time_slot.split(':'))
        start_time = datetime.combine(date, time(start_hour, start_minute))  # Crée la date complète avec l'heure
        end_time = start_time + timedelta(hours=2)  # Durée fixe de 2 heures pour chaque créneau

        # Affecte les valeurs au modèle
        self.instance.start_time = start_time
        self.instance.end_time = end_time

        return super().save(commit)


class WorkoutScheduleAdmin(admin.ModelAdmin):
    form = WorkoutScheduleForm  # Associe le formulaire personnalisé
    list_display = ['workout', 'start_time', 'end_time', 'location', 'coach', 'available', 'expired', 'complet']
    fields = ['workout', 'location', 'coach', 'participants', 'available', 'expired', 'date', 'time_slot', 'complet']  # Ajoutez 'date' et 'time_slot'
    filter_horizontal = ['participants']  # Pour ajouter des participants

    def save_model(self, request, obj, form, change):
        # Utilisez le comportement de sauvegarde défini dans le formulaire
        super().save_model(request, obj, form, change)
        obj.update_complet()  # Met à jour la disponibilité après la sauvegarde




class CoachAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'user', 'available', 'exp']
    filter_horizontal = ['specialties']
    search_fields = ['username', 'user__username']

class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'city', 'state', 'postal_code']

class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_available', 'description', 'price', 'duration', 'image']

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plan', 'start_date', 'payment_status']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'workout', 'content']

# admin.site.register(Booking, BookingAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Workout, WorkoutAdmin)
admin.site.register(WorkoutImage)
admin.site.register(Coach, CoachAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(WorkoutSchedule, WorkoutScheduleAdmin)


