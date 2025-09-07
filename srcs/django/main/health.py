"""
Health check views for Docker health checks
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
from django.conf import settings


def health_check(request):
    """
    Health check endpoint for Docker
    Returns 200 if all services are healthy
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }, status=503)
    
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
