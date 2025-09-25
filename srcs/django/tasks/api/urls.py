from django.urls import path
from ninja import NinjaAPI
from .controllers import router

# Task Management API Configuration
api = NinjaAPI(
    title="Task Management API",
    version="1.0.0",
    description="API para gestión de tareas - CRUD completo + Operaciones",
    urls_namespace="tasks_api",
    docs_url="/docs",
)

# Add consolidated task router
api.add_router("/", router)

# URL patterns
urlpatterns = [
    path("", api.urls),
]

"""
Task Management API Endpoints:

DJANGO NINJA API ROUTES:
* GET /api/tasks/                           -> List tasks with filtering, search, pagination
* POST /api/tasks/                          -> Create new task
* GET /api/tasks/tasks/{task_id}/           -> Get specific task details
* PUT /api/tasks/{task_id}/                 -> Update specific task (full update)
* PATCH /api/tasks/{task_id}/               -> Update specific task (partial update)
* DELETE /api/tasks/{task_id}/              -> Delete specific task (soft delete)

TASK ASSIGNMENTS:
* POST /api/tasks/{task_id}/assign/         -> Assign users to task
* DELETE /api/tasks/{task_id}/assign/{user_id}/ -> Unassign user from task
* GET /api/tasks/{task_id}/assignments/     -> Get task assignments

TASK COMMENTS:
* POST /api/tasks/{task_id}/comments/       -> Add comment to task
* GET /api/tasks/{task_id}/comments/        -> Get task comments (with pagination)

TASK HISTORY:
* GET /api/tasks/{task_id}/history/         -> Get task history (with pagination)

DOCUMENTATION:
* http://localhost:8000/api/tasks/docs         -> Swagger/OpenAPI Documentation
* http://localhost:8000/api/tasks/openapi.json -> OpenAPI Specification

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

HISTORY FILTERING:
* action: Filter by action type (created, updated, assigned, unassigned, status_changed, archived)
"""
