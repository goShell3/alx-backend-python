from django.apps import AppConfig
from django.core.signals import setting_changed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from models import Notification, Message, MessageHistory, User


@receiver(post_save, sender=Message)
def notification_login_user(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(post_save, sender=Message)
def log_content_before_log(sender, instance, updated, **kwargs):
    if not instance.pk:
        return  # it's a new message, not an update

    try:
        original = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return  # just to be safe

    if original.content != instance.content:
        MessageHistory.objects.create(
            message=instance,
            old_content=original.content
        )
        instance.edited = True


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    # Should be unnecessary if CASCADE is set, but here for safety/logging
    Message.objects.filter(sender=instance).delete()
    Notification.objects.filter(user=instance).delete()