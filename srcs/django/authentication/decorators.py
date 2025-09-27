"""
Custom decorators for API authentication
"""

from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test


def api_login_required(view_func):
    """
    Decorator for API views that require authentication.
    Returns JSON 401 instead of redirecting to login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required"}, 
                status=401
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def api_staff_required(view_func):
    """
    Decorator for API views that require staff/admin permissions.
    Returns JSON 403 for unauthorized users.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required"}, 
                status=401
            )
        if not request.user.is_staff:
            return JsonResponse(
                {"status": "error", "message": "Administrator permissions required"}, 
                status=403
            )
        return view_func(request, *args, **kwargs)
    return wrapper