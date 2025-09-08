"""
URL configuration for task management system.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    """Health check endpoint for Docker"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception:
        db_status = "error"
    
    try:
        # Check Redis connection
        cache.set("health_check", "ok", 30)
        redis_status = "healthy" if cache.get("health_check") == "ok" else "error"
    except Exception:
        redis_status = "error"
    
    if db_status == "healthy" and redis_status == "healthy":
        return JsonResponse({
            "status": "healthy",
            "database": db_status,
            "redis": redis_status
        })
    else:
        return JsonResponse({
            "status": "unhealthy",
            "database": db_status,
            "redis": redis_status
        }, status=503)

urlpatterns = [
    # Health check
    path("health/", health_check, name="health_check"),
    
    # Admin panel
    path("admin/", admin.site.urls),
    
    # Authentication web interface (templates)
    path("", include("authentication.web.urls")),
    
    # Authentication API endpoints
    path("api/auth/", include("authentication.api.urls")),
    
    # User management API endpoints  
    path("api/users/", include("authentication.api.user_urls")),
    
    # Task management API endpoints
    path("api/tasks/", include("tasks.api.urls")),
    
    # Task management web interface (templates)
    path("tasks/", include("tasks.web.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
