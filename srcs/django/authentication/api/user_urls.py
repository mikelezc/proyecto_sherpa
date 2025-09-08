from django.urls import path
from ninja import NinjaAPI
from authentication.api.controllers.user_controller import router as user_router

# User Management API Configuration
api = NinjaAPI(
    title="User Management API",
    version="1.0.0",
    description="API para gestión de usuarios",
    urls_namespace="users_api",
    docs_url="/docs",
)

# Add user router to root level to match /api/users/ routes
api.add_router("/", user_router)

# URL patterns
urlpatterns = [
    path("", api.urls),
]

"""
User Management API Endpoints (following subject requirements):

* GET /api/users/           -> List users with pagination  
* GET /api/users/{id}/      -> Get specific user
* PUT /api/users/{id}/      -> Update specific user
* GET /api/users/me/        -> Get current user profile

Documentation:
* http://localhost:8000/api/users/docs         -> Swagger/OpenAPI Documentation
* http://localhost:8000/api/users/openapi.json -> OpenAPI Specification
"""
