from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CounselorProfile

# accounts/signals.py

#@receiver(post_save, sender=CustomUser)
def create_counselor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'counselor':
        CounselorProfile.objects.get_or_create(user=instance)