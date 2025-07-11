from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""

    user_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        primary_key=True
    )

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        help_text=_('User email address')
    )

    password = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text=_('User password')
    )
    
    # profile_picture = models.ImageField(
    #     upload_to='profile_pictures/',
    #     null=True,
    #     blank=True,
    #     help_text=_('User profile picture')
    # )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text=_('Short biography about the user')
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text=_('User contact number')
    )
    is_online = models.BooleanField(
        default=False,
        help_text=_('User online status')
    )
    last_seen = models.DateTimeField(
        auto_now=True,
        help_text=_('Last time user was active')
    )
    status = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('User status message')
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


class Conversation(models.Model):
    """Conversation between two or more users."""
    conversation_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        primary_key=True
    )

    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        participant_usernames = ", ".join([user.username for user in self.participants.all()])
        return f"Conversation between: {participant_usernames}"


class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(
            recipient=user,
            read=False
        ).only('id', 'sender', 'content', 'timestamp')
    
class Message(models.Model):
    """Message sent in a conversation."""
    message_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        primary_key=True
    )

    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='message_receiver',
        on_delete=models.CASCADE
    )
    edited = models.BooleanField(
        default=False
    )
    
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager() 

    def __str__(self):
        return f"{self.sender.username}: {self.message_body[:30]}..."

class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

class Notification(models.Model):
    sender = models.ForeignKey(
        User, 
        related_name='message_sender',
        on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        User, 
        related_name='receive_message',
        on_delete=models.CASCADE)
    content = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} : {self.message.message_body} "
    
