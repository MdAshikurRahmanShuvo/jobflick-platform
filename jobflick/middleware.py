from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone


class AutoLogoutMiddleware:
    """Logs out users automatically after AUTO_LOGOUT_DELAY seconds of inactivity."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now().timestamp()
            last_activity = request.session.get("last_activity")
            max_idle = getattr(settings, "AUTO_LOGOUT_DELAY", 3600)

            if last_activity and now - last_activity > max_idle:
                logout(request)
                request.session.flush()
            else:
                request.session["last_activity"] = now

        response = self.get_response(request)
        return response
