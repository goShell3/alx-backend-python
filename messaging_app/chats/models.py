from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser.
    
    Additional fields:
    - profile_picture: User's profile image
    - bio: Short user biography
    - phone_number: Contact number
    - is_online: User's online status
    - last_seen: Timestamp of last activity
    - status: User's current status message
    """
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text=_('User profile picture')
    )
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
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name

class Chat(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='chats')

    def __str__(self):
        return self.name

class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.conversation}"

class Conversation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    messages = models.ManyToManyField(Message, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender} - {self.receiver}"
