from django.urls import path
from ninja import NinjaAPI
from .controllers.task_controller import router as task_router

# Task Management API Configuration
api = NinjaAPI(
    title="Task Management API",
    version="1.0.0",
    description="API para gestión de tareas - CRUD completo",
    urls_namespace="tasks_api",
    docs_url="/docs",
)

# Add task router
api.add_router("/", task_router)

# URL patterns
urlpatterns = [
    path("ninja/", api.urls),
]

"""
Task Management API Endpoints:

DJANGO NINJA (New API):
* http://localhost:8000/api/tasks/ninja/docs         -> Swagger/OpenAPI Documentation
* http://localhost:8000/api/tasks/ninja/openapi.json -> OpenAPI Specification

TASK CRUD:
* GET    /api/tasks/ninja/               -> List tasks (with filtering, search, pagination)
* POST   /api/tasks/ninja/               -> Create new task
* GET    /api/tasks/ninja/{id}/          -> Get task details
* PUT    /api/tasks/ninja/{id}/          -> Update task (full update)
* PATCH  /api/tasks/ninja/{id}/          -> Update task (partial update)
* DELETE /api/tasks/ninja/{id}/          -> Delete task (soft delete)

FILTERING PARAMETERS:
* search: Search in title and description
* status: Filter by status (todo, in_progress, review, done, cancelled)
* priority: Filter by priority (low, medium, high, critical)
* assigned_to: Filter by assigned user ID
* created_by: Filter by creator user ID
* tag: Filter by tag name
* is_overdue: Filter by overdue status (true/false)
* page: Page number (default: 1)
* page_size: Items per page (default: 20, max: 100)
"""
