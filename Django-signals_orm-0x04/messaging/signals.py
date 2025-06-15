from django.apps import AppConfig
from django.core.signals import setting_changed
from django.db.models.signals import post_save
from django.dispatch import receiver

from models import Notification, User


@receiver(post_save, sender=User)
def notification_login_user(sender, instance, **kwargs):
    if instance.user:
        print(f"{instance.user}: saved ")