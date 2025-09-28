import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    sent_at = django_filters.DateTimeFromToRangeFilter()
    sender = django_filters.CharFilter(field_name='sender__user_id')
    conversation = django_filters.CharFilter(field_name='conversation__conversation_id')

    class Meta:
        model = Message
        fields = ['sent_at', 'sender', 'conversation']
