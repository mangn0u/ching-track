"""
Signal: create UserPreferences when a new user is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import CustomUser
from apps.budgets.models import UserPreferences


@receiver(post_save, sender=CustomUser)
def create_user_preferences(sender, instance, created, **kwargs):
    """Auto-create UserPreferences row when a user registers."""
    if created:
        UserPreferences.objects.create(user=instance)
