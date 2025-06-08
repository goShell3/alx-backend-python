import django_filters
from .models import Conversation, Message
from django.contrib.auth.models import User
from django_filters import rest_framework as filters


class MessageFilter(django_filters.FilterSet):
    
    sender = filters.ModelChoiceFilter(queryset=User.objects.all())
    conversation = filters.UUIDFilter(field_name='conversation__conversation_id')
    start_date = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    is_read = filters.BooleanFilter()

    class Meta:
        model = Message
        fields = ["conversation", "sender", 'start_date', 'end_date']
