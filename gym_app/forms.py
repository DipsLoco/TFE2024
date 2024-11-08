from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User, WorkoutSchedule, WorkoutParticipation, Message
from django.core.exceptions import ValidationError
from django import forms
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

# Formulaire pour la participation aux séances de workout
class WorkoutParticipationForm(forms.ModelForm):
    """Formulaire pour indiquer la présence à une séance."""
    class Meta:
        model = WorkoutParticipation
        fields = ['present']
        widgets = {
            'present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Validation de l'horaire sans conflit de location
def clean(self):
    """Validation pour éviter le chevauchement de créneaux dans la même location."""
    cleaned_data = super().clean()
    location = cleaned_data.get('location')
    start_time = cleaned_data.get('start_time')
    end_time = cleaned_data.get('end_time')

    if location and start_time and end_time:
        # Recherche des séances en conflit avec la même location et des horaires qui se chevauchent
        conflicting_schedule = WorkoutSchedule.objects.filter(
            location=location,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(id=self.instance.id)
        
        # Si un conflit est trouvé, une erreur est levée
        if conflicting_schedule.exists():
            raise ValidationError("Cette location est déjà réservée pour l'heure sélectionnée.")
    
    return cleaned_data

# Formulaire pour la gestion des séances de workout
class WorkoutScheduleForm(forms.ModelForm):
    """Formulaire pour la création et modification de séances de workout."""
    schedule_choice = forms.ChoiceField(
        label="Choisissez un autre créneau",
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
        super().__init__(*args, **kwargs)
        
        # Configuration des choix de créneaux horaires si fourni
        if schedule:
            self.fields['schedule_choice'].choices = [
                (s.id, f"{s.start_time.strftime('%d %b %Y %H:%M')}") for s in schedule
            ]
        
        # Configuration de la liste de participants selon le rôle de l'utilisateur
        if user and user.role == 'coach':
            self.fields['participants'].queryset = User.objects.filter(role='member').only('first_name', 'last_name', 'email')
        else:
            self.fields['participants'].queryset = User.objects.all()

        # Génération dynamique des créneaux horaires pour le jour actuel
        today = timezone.now().date()
        time_slots = [
            (f"{today} 08:00", "8h-10h"),
            (f"{today} 10:00", "10h-12h"),
            (f"{today} 12:00", "12h-14h"),
            (f"{today} 14:00", "14h-16h"),
            (f"{today} 16:00", "16h-18h"),
        ]
        # Conversion des créneaux pour l'affichage des jours et horaires
        self.fields['schedule_choice'].choices = [(slot[0], f"{today.strftime('%A %d %B')} {slot[1]}") for slot in time_slots]

    def clean_participants(self):
        """Vérifie que le nombre de participants ne dépasse pas la limite."""
        participants = self.cleaned_data.get('participants')
        if participants and len(participants) > self.max_participants:
            raise ValidationError(f"Ce cours est complet avec un maximum de {self.max_participants} participants.")
        return participants

    def save(self, commit=True):
        """Sauvegarde en utilisant les informations du créneau choisi."""
        schedule_instance = super().save(commit=False)
        schedule_id = self.cleaned_data['schedule_choice']
        schedule = WorkoutSchedule.objects.get(id=schedule_id)
        
        # Mise à jour des informations de créneau pour le nouvel objet WorkoutSchedule
        schedule_instance.coach = schedule.coach
        schedule_instance.location = schedule.location
        schedule_instance.start_time = schedule.start_time
        schedule_instance.end_time = schedule.end_time
        
        if commit:
            schedule_instance.save()
            self.save_m2m()  # Sauvegarde des relations ManyToMany (participants)
        
        return schedule_instance


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
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'image', 'social_url']
        widgets = {
            'image': forms.ClearableFileInput(attrs={}),  # Retire l'attribut multiple si un seul fichier est nécessaire
        }
