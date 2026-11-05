from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import email_confirmed
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

@receiver(email_confirmed)
def on_email_confirmed(request, email_address, **kwargs):
    user = email_address.user
    if hasattr(user, 'profile'):
        user.profile.email_verified = True
        user.profile.save()

