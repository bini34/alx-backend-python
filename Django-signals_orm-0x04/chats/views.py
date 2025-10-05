from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View
from messaging.models import Message
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

User = get_user_model()

@cache_page(60)
def conversation_messages(request, user_id):
	"""Return messages to/from a user with minimal queries and 60s caching."""
	if request.method != 'GET':
		return JsonResponse({'detail': 'Method not allowed'}, status=405)
	try:
		user = User.objects.get(pk=user_id)
	except User.DoesNotExist:
		return JsonResponse({'detail': 'User not found'}, status=404)

	msgs = (
		Message.objects.filter(receiver=user)
		.select_related('sender', 'receiver')
		.prefetch_related(Prefetch('replies'))
		.order_by('-timestamp')[:100]
	)
	data = [
		{
			'id': m.id,
			'sender': getattr(m.sender, 'username', str(m.sender)),
			'receiver': getattr(m.receiver, 'username', str(m.receiver)),
			'content': m.content,
			'timestamp': m.timestamp.isoformat(),
			'edited': m.edited,
			'read': m.read,
			'replies': [r.id for r in m.replies.all()],
		}
		for m in msgs
	]
	return JsonResponse({'results': data})
