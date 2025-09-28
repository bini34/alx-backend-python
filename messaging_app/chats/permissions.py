from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """Allow only participants of a conversation to access or modify messages."""
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return request.user.is_authenticated and obj.participants.filter(user_id=request.user.user_id).exists()
        if hasattr(obj, 'conversation'):
            return request.user.is_authenticated and obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        return False
