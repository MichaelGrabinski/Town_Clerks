from __future__ import annotations

from urllib.parse import urlencode

from django.utils.deprecation import MiddlewareMixin

from .models import ActivityLog


def _client_ip(request):
    # Respect typical proxy headers if present.
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or ''


class ActivityLogMiddleware(MiddlewareMixin):
    """Log each request to the app for auditing.

    Notes:
      - Avoids logging static files.
      - Avoids logging the admin login page to reduce noise.
    """

    def process_response(self, request, response):
        try:
            path = request.path or ''
            if path.startswith('/static/'):
                return response

            user = getattr(request, 'user', None)
            username = ''
            user_id = None
            if user is not None and getattr(user, 'is_authenticated', False):
                username = user.get_username() or ''
                user_id = user.pk

            qs = request.GET.dict() if hasattr(request, 'GET') else {}
            # Keep query string compact; avoid huge values.
            qs_encoded = urlencode({k: (v[:200] if isinstance(v, str) else v) for k, v in qs.items()})

            ActivityLog.objects.create(
                user_id=user_id,
                username=username,
                event_type='request',
                action='',
                path=path[:500],
                method=(request.method or '')[:10],
                status_code=getattr(response, 'status_code', None),
                ip_address=_client_ip(request)[:64],
                user_agent=(request.META.get('HTTP_USER_AGENT', '') or '')[:2000],
                referer=(request.META.get('HTTP_REFERER', '') or '')[:500],
                query_string=qs_encoded[:2000],
            )
        except Exception:
            # Never break the response due to logging.
            return response

        return response
