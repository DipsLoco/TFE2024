from datetime import datetime, timedelta, time
from mailbox import Message
from django.shortcuts import render
from django.utils import timezone
from django.contrib import admin
from django import forms
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import User, Workout, Coach, Location, Plan, Subscription, Review, WorkoutImage, WorkoutParticipation, WorkoutSchedule, Message, CatalogService, PersonalizedCoaching, GymAccessory, DietPlan
from django.contrib.admin import AdminSite
from django.urls import path
from django.utils.html import format_html
from django.db.models import Count
from .models import WorkoutSchedule, WorkoutParticipation

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


@admin.register(WorkoutParticipation)
class WorkoutParticipationAdmin(admin.ModelAdmin):
    list_display = ['workout_schedule', 'participant', 'present']
    list_filter = ['present', 'workout_schedule__start_time']
    search_fields = ['participant__username', 'workout_schedule__workout__title']

class MyAdminSite(AdminSite):
    site_header = 'Gestion des séances BE-FIT'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('workout-statistics/', self.admin_view(self.workout_statistics), name='workout_statistics'),
        ]
        return custom_urls + urls

    def workout_statistics(self, request):
        # Récupérer toutes les séances avec leur taux de présence
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
        
        # Affichage des statistiques dans le tableau de bord
        output = format_html(
            "<h2>Statistiques des séances</h2><table class='table'><thead><tr><th>Séance</th><th>Participants</th><th>Présents</th><th>Absents</th></tr></thead><tbody>"
        )
        for stat in stats:
            output += format_html(
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
                stat['schedule'].workout.title,
                stat['total_participants'],
                stat['present_count'],
                stat['absence_count'],
            )
        output += format_html("</tbody></table>")
        return render(request, 'admin/workout_statistics.html', {'stats': stats, 'output': output})

# Activer la personnalisation dans admin
admin_site = MyAdminSite(name='myadmin')







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


# Administration pour le modèle Message
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'sender', 'recipient')  # Ajouter des filtres pour faciliter la recherche
    search_fields = ('subject', 'sender__username', 'recipient__username', 'body')  # Permettre la recherche par sujet, expéditeur et destinataire


# admin.site.register(Booking, BookingAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Workout, WorkoutAdmin)
admin.site.register(WorkoutImage)
admin.site.register(Coach, CoachAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(WorkoutSchedule, WorkoutScheduleAdmin,)
admin.site.register(Message, MessageAdmin)
admin.site.register(CatalogService)
admin.site.register(PersonalizedCoaching)
admin.site.register(GymAccessory)
admin.site.register(DietPlan)



