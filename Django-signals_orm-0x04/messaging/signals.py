from django.apps import AppConfig
from django.core.signals import setting_changed
from django.db.models.signals import post_save
from django.dispatch import receiver

from models import Notification, Message


@receiver(post_save, sender=Message)
def notification_login_user(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
