from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import CustomerProfile, Hospital

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """
    Create a CustomerProfile automatically when a new User is created.
    This will be called for all new users initially.
    """
    if created:
        # Create a basic CustomerProfile
        CustomerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    """
    Ensure the CustomerProfile is saved when the User is saved.
    """
    if hasattr(instance, 'customer_profile'):
        instance.customer_profile.save()
