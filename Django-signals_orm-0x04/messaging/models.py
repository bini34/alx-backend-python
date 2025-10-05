from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UnreadMessagesManager(models.Manager):
	def for_user(self, user):
		return self.get_queryset().filter(receiver=user, read=False).only('id', 'sender', 'content', 'timestamp')


class Message(models.Model):
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
	content = models.TextField()
	timestamp = models.DateTimeField(default=timezone.now)
	edited = models.BooleanField(default=False)
	read = models.BooleanField(default=False)
	parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

	objects = models.Manager()
	unread = UnreadMessagesManager()

	def __str__(self):
		return f"From {self.sender} to {self.receiver}: {self.content[:20]}"


class Notification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
	message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
	created_at = models.DateTimeField(auto_now_add=True)
	seen = models.BooleanField(default=False)

	def __str__(self):
		return f"Notification for {self.user} - Message {self.message_id}"


class MessageHistory(models.Model):
	message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
	old_content = models.TextField()
	edited_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"History of Message {self.message_id} at {self.edited_at}"
