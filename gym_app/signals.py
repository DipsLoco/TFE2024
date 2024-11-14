# gym_app/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message


User = get_user_model()

# Signal pre_save pour stocker l'ancien mot de passe
@receiver(pre_save, sender=User)
def store_original_password(sender, instance, **kwargs):
    # On ne fait rien si l'utilisateur est nouveau (instance.pk est None)
    if instance.pk:
        old_user = sender.objects.get(pk=instance.pk)
        # Si le mot de passe a changé, on stocke l'ancien mot de passe
        if old_user.password != instance.password:
            instance.__original_password = old_user.password
        else:
            instance.__original_password = old_user.password
    else:
        # Dans le cas où l'utilisateur est nouveau, pas de mot de passe précédent
        instance.__original_password = instance.password
User = get_user_model()

@receiver(pre_save, sender=User)
def check_password_change(sender, instance, **kwargs):
    if instance.pk:  # Si l'utilisateur existe déjà
        try:
            old_user = sender.objects.get(pk=instance.pk)
            if old_user.password != instance.password:
                instance._password_changed = True  # Marque que le mot de passe a changé
            else:
                instance._password_changed = False
        except sender.DoesNotExist:
            instance._password_changed = False
    else:
        instance._password_changed = False  # Cas d'un nouvel utilisateur

@receiver(post_save, sender=User)
def send_password_change_notification(sender, instance, created, **kwargs):
    if hasattr(instance, '_password_changed') and instance._password_changed:
        try:
            admin_user = sender.objects.filter(is_staff=True).first()  # Récupère un administrateur

            if admin_user:
                # Création d'un message de notification pour l'utilisateur qui a changé son mot de passe
                Message.objects.create(
                    sender=admin_user,
                    recipient=instance,
                    subject="Modification de votre mot de passe",
                    body="Votre mot de passe a été modifié avec succès. Si vous n'êtes pas à l'origine de ce changement, veuillez contacter l'administrateur.",
                    is_important=True  # On marque ce message comme important
                )
                print(f"Message envoyé à {instance.username}.")

            else:
                print("[Erreur] Aucun administrateur trouvé pour envoyer le message.")
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de changement de mot de passe : {e}")



