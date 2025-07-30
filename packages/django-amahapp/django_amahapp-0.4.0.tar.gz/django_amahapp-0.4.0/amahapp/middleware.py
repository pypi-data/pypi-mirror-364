import time
from .models import UserActivityLog

class UserActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        if not request.path.startswith('/admin/'):
            UserActivityLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                path=request.path,
                method=request.method,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                duration=round(duration, 3),
            )
        return response
