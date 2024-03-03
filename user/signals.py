from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import  User


@receiver(post_save, sender=User)
def createProfile(sender, instance, **kwargs):
    user = User.objects.get(username=instance.username)
    if not Profile.objects.filter(user=user).exists():
        profile = Profile(user=user)
        profile.save()
