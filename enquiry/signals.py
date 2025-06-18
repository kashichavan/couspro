from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import Counsellor

@receiver(post_save, sender=CustomUser)
def create_counsellor_for_user(sender, instance, created, **kwargs):
    if created and instance.role == 'counselor':
        Counsellor.objects.create(user=instance, mobile='', department='')



# enquiry/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils.timezone import localdate
from .models import Enquiry

@receiver([post_save, post_delete], sender=Enquiry)
def clear_enquiry_cache(sender, instance, **kwargs):
    """
    Clears related cached entries whenever Enquiry is saved or deleted.
    """
    print("[SIGNAL] Clearing cache due to Enquiry save/delete")

    # Always clear these caches
    cache.delete('joined_students')
    cache.delete('dropout_students')
    cache.delete('pending_enquiries')
    cache.delete('enquiry_list_view')

    # Clear today's followups cache if relevant
    if instance.followup_date:
        today_key = f'today_followups_{instance.followup_date}'
        cache.delete(today_key)

    # (Optional) Clear today's followups if date matches today (safe fallback)
    today_key = f'today_followups_{localdate()}'
    cache.delete(today_key)
