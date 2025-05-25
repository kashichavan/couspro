from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import Counsellor

@receiver(post_save, sender=CustomUser)
def create_counsellor_for_user(sender, instance, created, **kwargs):
    if created and instance.role == 'counselor':
        Counsellor.objects.create(user=instance, mobile='', department='')
