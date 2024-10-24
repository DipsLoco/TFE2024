from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User, WorkoutSchedule, WorkoutParticipation, Message
from django import forms
import re

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']  # Les champs que l'utilisateur doit remplir
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objet'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 5}),
        }

class WorkoutParticipationForm(forms.ModelForm):
    class Meta:
        model = WorkoutParticipation
        fields = ['present']
        widgets = {
            'present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class WorkoutScheduleForm(forms.ModelForm):
    schedule_choice = forms.ChoiceField(
        label="Choisissez un autre créneau",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})  # Ajout de la classe CSS
    )

    class Meta:
        model = WorkoutSchedule
        fields = ['schedule_choice']

    def __init__(self, *args, **kwargs):
        schedule = kwargs.pop('schedule', None)
        super().__init__(*args, **kwargs)
        if schedule:
            # Remplir le champ de choix avec les créneaux horaires disponibles
            self.fields['schedule_choice'].choices = [
                (s.id, f"{s.start_time.strftime('%d %b %Y %H:%M')}") for s in schedule
            ]

    def save(self, commit=True):
        schedule_instance = super().save(commit=False)
        schedule_id = self.cleaned_data['schedule_choice']
        schedule = WorkoutSchedule.objects.get(id=schedule_id)
        
        # Mise à jour des champs liés au créneau sélectionné
        schedule_instance.coach = schedule.coach
        schedule_instance.location = schedule.location
        schedule_instance.start_time = schedule.start_time
        schedule_instance.end_time = schedule.end_time
        
        if commit:
            schedule_instance.save()
        return schedule_instance

class SignUpForm(UserCreationForm):
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

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'image', 'social_url']
        widgets = {
            'image': forms.ClearableFileInput(attrs={}),  # Retire l'attribut multiple si un seul fichier est nécessaire
        }
