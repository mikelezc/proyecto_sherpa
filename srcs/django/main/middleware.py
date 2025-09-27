"""
API CSRF Exemption Middleware

This middleware exempts specific API endpoints from CSRF protection
while maintaining security for web forms.
"""
import re
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware


class APICsrfExemptMiddleware(CsrfViewMiddleware):
    """
    Middleware that exempts API endpoints from CSRF protection.
    
    Uses CSRF_EXEMPT_URLS setting to determine which URLs to exempt.
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if the URL should be exempt from CSRF
        if hasattr(settings, 'CSRF_EXEMPT_URLS'):
            path = request.path_info.lstrip('/')
            
            for pattern in settings.CSRF_EXEMPT_URLS:
                if re.match(pattern, path):
                    # Mark this request as CSRF exempt
                    setattr(request, '_dont_enforce_csrf_checks', True)
                    return None
        
        # Use default CSRF behavior for non-exempt URLs
        return super().process_view(request, callback, callback_args, callback_kwargs)