import django_filters
from .models import Conversation, Message


class MessageFilter(django_filters.FilterSet):
    sender = django_filters.CharFilter(field_name='sender')

    class Meta:
        model = Message
        fields = ["conversation", "sender", "message_body"]