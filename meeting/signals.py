from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Meeting


@receiver(post_save, sender=Meeting)
def add_join_user(sender, created, instance, **kwargs):

    if created:
        instance.join_meeting.add(instance.user)