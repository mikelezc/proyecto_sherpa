"""
URL configuration for task management system.
Enterprise authentication and task management routes.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def health_check(request):
    """Simple health check endpoint for Docker"""
    return JsonResponse({"status": "healthy"})

urlpatterns = [
    # Health check
    path("health/", health_check, name="health_check"),
    
    # Admin panel
    path("admin/", admin.site.urls),
    
    # Authentication web interface (templates)
    path("", include("authentication.web.urls")),
    
    # Authentication API
    path("api/auth/", include("authentication.api.urls")),
    
    # Task management API
    path("api/tasks/", include("tasks.api.urls")),
    
    # Task management web interface (templates)
    path("tasks/", include("tasks.web.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
