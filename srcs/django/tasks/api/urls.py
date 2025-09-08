from django.urls import path
from ninja import NinjaAPI
from .controllers.task_controller import router as task_router
from .controllers.task_operations_controller import router as task_operations_router

# Task Management API Configuration
api = NinjaAPI(
    title="Task Management API",
    version="1.0.0",
    description="API para gestión de tareas - CRUD completo + Operaciones",
    urls_namespace="tasks_api",
    docs_url="/docs",
)

# Add task router
api.add_router("/", task_router)
# Add task operations router 
api.add_router("/", task_operations_router)

# URL patterns
urlpatterns = [
    path("", api.urls),  # Changed from "ninja/" to "" to match /api/tasks/ directly
]

"""
Task Management API Endpoints (following subject requirements):

DJANGO NINJA API:
* GET /api/tasks/                    -> List tasks with filtering, search, pagination
* POST /api/tasks/                   -> Create new task
* GET /api/tasks/{id}/               -> Get specific task
* PUT /api/tasks/{id}/               -> Update specific task (full update)
* PATCH /api/tasks/{id}/             -> Update specific task (partial update)
* DELETE /api/tasks/{id}/            -> Delete specific task
* POST /api/tasks/{id}/assign/       -> Assign task to user
* POST /api/tasks/{id}/comments/     -> Add comment to task
* GET /api/tasks/{id}/comments/      -> Get task comments
* GET /api/tasks/{id}/history/       -> Get task history

Documentation:
* http://localhost:8000/api/tasks/docs         -> Swagger/OpenAPI Documentation
* http://localhost:8000/api/tasks/openapi.json -> OpenAPI Specification

TASK CRUD:
* GET    /api/tasks/ninja/               -> List tasks (with filtering, search, pagination)
* POST   /api/tasks/ninja/               -> Create new task
* GET    /api/tasks/ninja/{id}/          -> Get task details
* PUT    /api/tasks/ninja/{id}/          -> Update task (full update)
* PATCH  /api/tasks/ninja/{id}/          -> Update task (partial update)
* DELETE /api/tasks/ninja/{id}/          -> Delete task (soft delete)

TASK OPERATIONS:
* POST   /api/tasks/ninja/{id}/assign/   -> Assign users to task
* POST   /api/tasks/ninja/{id}/comments/ -> Add comment to task
* GET    /api/tasks/ninja/{id}/comments/ -> List task comments (with pagination)
* GET    /api/tasks/ninja/{id}/history/  -> List task history (with pagination)

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
