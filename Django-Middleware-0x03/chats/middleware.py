import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict, deque

# Logging User Requests Middleware
class RequestLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request_logger')
        handler = logging.FileHandler('requests.log')
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        self.logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        return self.get_response(request)

# Restrict Chat Access by Time Middleware
class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        if time(21, 0) <= now or now <= time(6, 0):
            if request.path.startswith('/api/'):
                return HttpResponseForbidden('Chat access is restricted during these hours.')
        return self.get_response(request)

# Offensive Language/Rate Limiting Middleware
class OffensiveLanguageMiddleware(MiddlewareMixin):
    message_counts = defaultdict(lambda: deque())

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/api/messages'):
            ip = request.META.get('REMOTE_ADDR')
            now = datetime.now()
            # Remove timestamps older than 1 minute
            while self.message_counts[ip] and (now - self.message_counts[ip][0]).total_seconds() > 60:
                self.message_counts[ip].popleft()
            if len(self.message_counts[ip]) >= 5:
                return HttpResponseForbidden('Rate limit exceeded: 5 messages per minute.')
            self.message_counts[ip].append(now)
        return self.get_response(request)

# Role Permission Middleware
class RolepermissionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/messages') and request.method in ['DELETE', 'PUT', 'PATCH']:
            user = request.user
            if not user.is_authenticated or user.role not in ['admin', 'moderator']:
                return HttpResponseForbidden('You do not have permission to perform this action.')
        return self.get_response(request)
