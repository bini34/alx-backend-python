

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
	queryset = Conversation.objects.all()
	serializer_class = ConversationSerializer
	permission_classes = [IsAuthenticated, IsParticipantOfConversation]

	def create(self, request, *args, **kwargs):
		participant_ids = request.data.get('participants', [])
		participants = User.objects.filter(user_id__in=participant_ids)
		conversation = Conversation.objects.create()
		conversation.participants.set(participants)
		serializer = self.get_serializer(conversation)
		return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
	queryset = Message.objects.all()
	serializer_class = MessageSerializer
	permission_classes = [IsAuthenticated, IsParticipantOfConversation]
	filter_backends = [DjangoFilterBackend]
	filterset_class = MessageFilter
	pagination_class = MessagePagination

	def create(self, request, *args, **kwargs):
		sender_id = request.data.get('sender')
		conversation_id = request.data.get('conversation')
		message_body = request.data.get('message_body')
		sender = User.objects.get(user_id=sender_id)
		conversation = Conversation.objects.get(conversation_id=conversation_id)
		message = Message.objects.create(
			sender=sender,
			conversation=conversation,
			message_body=message_body,
		)
		serializer = self.get_serializer(message)
		return Response(serializer.data, status=status.HTTP_201_CREATED)
