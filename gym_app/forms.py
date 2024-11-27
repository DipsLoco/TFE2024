from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User, WorkoutSchedule, WorkoutParticipation, Message
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm
import re


# Formulaire pour l'envoi de messages
class MessageForm(forms.ModelForm):
    """Formulaire pour créer un message avec un objet et un corps du message."""
    class Meta:
        model = Message
        fields = ['subject', 'body']  # Champs requis pour le formulaire
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objet'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 5}),
        }



from datetime import datetime, timedelta, time
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import WorkoutSchedule, WorkoutParticipation, User, Workout

class WorkoutScheduleForm(forms.ModelForm):
    """Formulaire pour la création et modification de séances de workout avec validation des créneaux et gestion des participants."""
    schedule_choice = forms.ChoiceField(
        label="Choisissez un créneau",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    max_participants = 10  # Limite de participants par séance

    class Meta:
        model = WorkoutSchedule
        fields = ['workout', 'start_time', 'end_time', 'location', 'participants', 'schedule_choice', 'available', 'expired', 'complet']
        widgets = {
            'participants': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'start_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Heure de début'}),
            'end_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Heure de fin'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        schedule = kwargs.pop('schedule', None)
        workout_queryset = kwargs.pop('workout_queryset', Workout.objects.all())
        super().__init__(*args, **kwargs)

        # Créneaux horaires pour les 6 prochains jours
        today = timezone.now().date()
        time_slots = [(8, 10), (10, 12), (14, 16), (16, 18)]
        schedule_choices = []
        for day_offset in range(6):
            date = today + timedelta(days=day_offset)
            for start_hour, end_hour in time_slots:
                start_time = timezone.make_aware(datetime.combine(date, time(start_hour)))
                end_time = timezone.make_aware(datetime.combine(date, time(end_hour)))
                schedule_choices.append((
                    start_time.strftime('%Y-%m-%d %H:%M'), 
                    f"{date.strftime('%A %d %B')} {start_hour}h-{end_hour}h"
                ))

        self.fields['schedule_choice'].choices = schedule_choices
        self.fields['participants'].required = False

        # Queryset pour les participants et les workouts selon le rôle
        if user and user.role in ['coach', 'admin']:
            self.fields['participants'].queryset = User.objects.filter(role='member').only('first_name', 'last_name', 'email')
            self.fields['workout'].queryset = workout_queryset
        else:
            self.fields['participants'].queryset = User.objects.all()

    def clean(self):
        """Validation des conflits d'horaires pour éviter les double réservations pour le coach."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        location = cleaned_data.get('location')
        coach = self.instance.coach if self.instance.pk else self.initial.get('user')

        # Vérification de conflit d'horaire pour la salle
        if location and start_time and end_time:
            conflicting_schedule = WorkoutSchedule.objects.filter(
                location=location,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(id=self.instance.id)
            
            if conflicting_schedule.exists():
                raise ValidationError(
                    "La salle sélectionnée est déjà réservée pour ce créneau. "
                    "Merci de choisir un autre créneau ou une autre salle."
                )

        # Vérification de conflit d'horaire pour le coach, même créneau mais pour lieu différent
        if coach and start_time and end_time:
            conflicting_coach_schedule = WorkoutSchedule.objects.filter(
                coach=coach,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(id=self.instance.id)
            
            if conflicting_coach_schedule.exists():
                raise ValidationError(
                    "Vous avez déjà une séance programmée à cette heure, pour ce lieu ou un autre. "
                    "Vous ne pouvez pas être à deux endroits différents à la même heure, le même jour, ou dans la même salle. "
                    "Merci de choisir un créneau horaire différent."
                )

        return cleaned_data

    def save(self, commit=True):
        """Sauvegarde en utilisant les informations du créneau choisi et assure l'enregistrement des participants."""
        schedule_instance = super().save(commit=False)
        
        # Utilise schedule_choice pour définir start_time et end_time
        schedule_choice_str = self.cleaned_data['schedule_choice']
        schedule_start_time = timezone.make_aware(datetime.strptime(schedule_choice_str, '%Y-%m-%d %H:%M'))
        schedule_end_time = schedule_start_time + timedelta(hours=2)
        
        # Mise à jour des heures de début et de fin pour l'instance WorkoutSchedule
        schedule_instance.start_time = schedule_start_time
        schedule_instance.end_time = schedule_end_time

        if commit:
            schedule_instance.save()
            self.save_m2m()  # Sauvegarde des relations ManyToMany (participants)
            schedule_instance.participants.set(self.cleaned_data['participants'])  # Liaison manuelle des participants
            print(f"Participants enregistrés : {self.cleaned_data['participants']}")
        
        return schedule_instance


class WorkoutParticipationForm(forms.ModelForm):
    """Formulaire pour indiquer la présence à une séance."""
    class Meta:
        model = WorkoutParticipation
        fields = ['present']
        widgets = {
            'present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



# Formulaire pour l'inscription des utilisateurs
class SignUpForm(UserCreationForm):
    """Formulaire d'inscription pour les utilisateurs, avec champs supplémentaires."""
    email = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse e-mail'})
    )
    first_name = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        label="Nom de famille",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'})
    )
    birth_date = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date de naissance', 'type': 'date'})
    )
    phone = forms.CharField(
        label="Numéro de téléphone",
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'})
    )
    address = forms.CharField(
        label="Adresse",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse'})
    )
    postal_code = forms.CharField(
        label="Code postal",
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code postal'})
    )
    city = forms.CharField(
        label="Ville",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'})
    )
    image = forms.ImageField(
        label="Image de profil",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'phone', 'address', 'postal_code', 'city', 'image', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Nom d\'utilisateur'
        self.fields['username'].label = 'Nom d\'utilisateur'
        self.fields['username'].help_text = 'Requis. 150 caractères ou moins. Lettres, chiffres et @/./+/-/_ uniquement.'
        
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Mot de passe'
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password1'].help_text = (
            'Votre mot de passe doit contenir au moins 8 caractères, ne pas être couramment utilisé, '
            'ne pas être entièrement numérique, contenir au moins une lettre majuscule, '
            'une lettre minuscule, un chiffre et un caractère spécial.'
        )

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmez le mot de passe'
        self.fields['password2'].label = 'Confirmez le mot de passe'
        self.fields['password2'].help_text = 'Entrez le même mot de passe que précédemment, pour vérification.'

    def clean_password1(self):
        """Validation personnalisée du mot de passe avec exigences spécifiques."""
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError('Votre mot de passe doit contenir au moins 8 caractères.')
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError('Votre mot de passe doit contenir au moins une lettre majuscule.')
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError('Votre mot de passe doit contenir au moins une lettre minuscule.')
        if not re.search(r'[0-9]', password1):
            raise forms.ValidationError('Votre mot de passe doit contenir au moins un chiffre.')
        if not re.search(r'[\W_]', password1):
            raise forms.ValidationError('Votre mot de passe doit contenir au moins un caractère spécial.')
        return password1

# Formulaire pour la mise à jour du profil utilisateur
class UserProfileForm(forms.ModelForm):
    """Formulaire pour modifier les informations de profil utilisateur."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'image', 'social_url', 'instagram_url']
        widgets = {
            'image': forms.ClearableFileInput(attrs={}),  # Retire l'attribut multiple si un seul fichier est nécessaire
        }



User = get_user_model()

class CustomPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe actuel",
        required=True
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nouveau mot de passe",
        required=True
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmer le mot de passe",
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 != new_password2:
            self.add_error('new_password2', "Les mots de passe ne correspondent pas.")
        
        if len(new_password1) < 8:
            self.add_error('new_password1', "Le mot de passe doit comporter au moins 8 caractères.")
        
        return cleaned_data


# Formulaire pour reinitialiser les mot de passe des user membre coach et admin

class PasswordResetForm(forms.Form):
    # Champ pour sélectionner l'utilisateur à réinitialiser
    user_select = forms.ModelChoiceField(queryset=User.objects.all(), label="Sélectionner un utilisateur", widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Champs pour le nouveau mot de passe
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Nouveau mot de passe")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmer le mot de passe")

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        # Vérification que les mots de passe correspondent
        if new_password1 != new_password2:
            self.add_error('new_password2', "Les mots de passe ne correspondent pas.")
        elif len(new_password1) < 8:
            self.add_error('new_password1', "Le mot de passe doit comporter au moins 8 caractères.")
        
        return cleaned_data
