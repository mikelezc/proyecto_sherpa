"""
Task Management API Controllers

HTTP request/response handlers for task operations.
"""

from typing import Optional
from django.core.paginator import Paginator
from ninja import Router

from ..services import TaskCrudOperations, TaskQueryBuilder
from ..infrastructure.serializers import (
    serialize_assignment,
    serialize_comment,
    serialize_task_list,
    serialize_task_detail,
    serialize_history
)

from .schemas import (
    # Task schemas
    TaskCreateSchema,
    TaskUpdateSchema, 
    TaskPatchSchema,
    TaskDetailSchema,
    PaginatedTasksSchema,
    TaskDeleteResponseSchema,
    # Operations schemas
    TaskAssignSchema,
    TaskAssignResponseSchema,
    TaskAssignmentSchema,
    CommentCreateSchema,
    CommentSchema,
    PaginatedCommentsSchema,
    TaskHistorySchema,
    PaginatedHistorySchema,
    # Common schemas
    TaskErrorSchema
)

router = Router()


def paginate_queryset(queryset, page, page_size=20):
    """Helper function to paginate a queryset and return pagination data"""
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    return {
        'page_obj': page_obj,
        'count': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    }


# ============================
# TASK CRUD OPERATIONS
# ============================

@router.get("/", response=PaginatedTasksSchema)
def list_tasks(request, page: int = 1, status: Optional[str] = None, priority: Optional[str] = None, 
               assigned_to_me: bool = False, search: Optional[str] = None):
    """
    Get paginated list of tasks with optional filtering
    
    DEFAULT FEATURES ENABLED:
    - Pagination: 20 tasks per page
    - Authentication: Login required
    - Auto-filtering: Excludes archived tasks
    - Query optimization: Reduces N+1 queries
    - Ordering: By creation date (newest first)
    
    AVAILABLE FILTERS:
    - status: 'todo', 'in_progress', 'review', 'done'
    - priority: 'low', 'medium', 'high', 'critical'  
    - assigned_to_me: true/false
    - search: Search in title and description (case-insensitive)
    
    RESPONSE INCLUDES:
    - Task basic info (id, title, status, priority, dates)
    - Creator and assigned users (minimal info)
    - Tags with colors
    - Overdue calculation
    """
    
    # Use the filter service to build the queryset
    filter_params = {
        'status': status,
        'priority': priority,
        'assigned_to_me': assigned_to_me,
        'user': request.user,
        'search': search
    }
    
    queryset = TaskQueryBuilder.build_from_params(**filter_params)
    
    # Pagination
    pagination = paginate_queryset(queryset, page)
    
    return PaginatedTasksSchema(
        results=[serialize_task_list(task) for task in pagination['page_obj']],
        count=pagination['count'],
        has_next=pagination['has_next'],
        has_previous=pagination['has_previous']
    )


@router.post("/", response=TaskDetailSchema)
def create_task(request, data: TaskCreateSchema):
    """
    Create a new task
    
    FEATURES:
    - Auto-assigns creator as task owner
    - Supports tags, team assignment, and parent task
    - Validates required fields and permissions
    
    REQUIRES: title, description, due_date
    OPTIONAL: assigned_to_ids, tag_ids, parent_task_id, team_id, metadata
    """
    task = TaskCrudOperations.create_task(request.user, data)
    return serialize_task_detail(task)


@router.get("/tasks/{task_id}", response=TaskDetailSchema, tags=["tasks"])
def get_task_by_id(request, task_id: int):
    """
    Get complete task details by ID
    
    INCLUDES:
    - Full task information and metadata
    - Creator and all assigned users
    - Tags, team, parent task relations
    - Calculated fields (is_overdue, etc.)
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    return serialize_task_detail(task)


@router.put("/{int:task_id}", response=TaskDetailSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    """
    Full task update (PUT) - replaces all fields
    
    FEATURES:
    - Updates all provided fields
    - Maintains task history/audit trail
    - Validates permissions and business rules
    
    UPDATABLE: title, description, status, priority, dates, assignments, tags
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    updated_task = TaskCrudOperations.update_task(task, request.user, data)
    return serialize_task_detail(updated_task)


@router.patch("/{int:task_id}", response=TaskDetailSchema)
def partial_update_task(request, task_id: int, data: TaskPatchSchema):
    """
    Partial task update (PATCH) - updates only provided fields
    
    COMMON USE CASES:
    - Quick status changes (todo → in_progress → done)
    - Priority adjustments
    - Time tracking (actual_hours updates)
    
    FIELDS: status, priority, actual_hours
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    updated_task = TaskCrudOperations.partial_update_task(task, data)
    return serialize_task_detail(updated_task)


@router.delete("/{int:task_id}", response=TaskDeleteResponseSchema)
def delete_task(request, task_id: int):
    """
    Delete task (soft delete - archives task)
    
    BEHAVIOR:
    - Sets is_archived=True (preserves data)
    - Maintains audit trail and history
    - Task remains in database for recovery
    
    NOTE: Physical deletion not available via API
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    TaskCrudOperations.archive_task(task)
    return TaskDeleteResponseSchema(success=True, message="Task archived successfully")


# ============================
# TASK OPERATIONS
# ============================

@router.post("/{int:task_id}/assign", response=TaskAssignResponseSchema)
def assign_task(request, task_id: int, data: TaskAssignSchema):
    """
    Assign users to a task
    
    FEATURES:
    - Multiple user assignment in single request
    - Primary assignee designation
    - Automatic notification sending
    
    BODY: {"user_ids": [1,2,3], "is_primary": false}
    """
    try:
        task = TaskQueryBuilder.get_task_with_relations(task_id)
        assignments = TaskCrudOperations.assign_users_to_task(
            task, data.user_ids, request.user, data.is_primary or False
        )
        
        return TaskAssignResponseSchema(
            success=True,
            message=f"Task assigned to {len(assignments)} users",
            assignments=[serialize_assignment(assignment) for assignment in assignments]
        )
        
    except Exception:
        return TaskErrorSchema(error="Task not found")


@router.delete("/{int:task_id}/assign/{int:user_id}")
def unassign_task(request, task_id: int, user_id: int):
    """
    Remove user assignment from task
    
    BEHAVIOR:
    - Removes specific user from task
    - Preserves assignment history
    - Returns success/error status
    """
    success = TaskCrudOperations.unassign_user_from_task(task_id, user_id)
    
    if success:
        return {"success": True, "message": "User unassigned successfully"}
    else:
        return {"error": "Assignment not found"}


@router.get("/{int:task_id}/assignments", response=list[TaskAssignmentSchema])
def get_task_assignments(request, task_id: int):
    """
    Get all current assignments for a task
    
    RETURNS:
    - List of assigned users with details
    - Assignment timestamps and assignor info
    - Primary assignee designation
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    assignments = TaskQueryBuilder.get_task_assignments(task)
    return [serialize_assignment(assignment) for assignment in assignments]


@router.post("/{int:task_id}/comments", response=CommentSchema)
def create_comment(request, task_id: int, data: CommentCreateSchema):
    """
    Add comment to task
    
    FEATURES:
    - Auto-assigns comment author
    - Supports markdown formatting
    - Triggers notifications to assignees
    
    BODY: {"content": "Comment text here"}
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    comment = TaskCrudOperations.create_comment(task, request.user, data.content)
    return serialize_comment(comment)


@router.get("/{int:task_id}/comments", response=PaginatedCommentsSchema)
def get_task_comments(request, task_id: int, page: int = 1):
    """
    Get paginated task comments (20 per page)
    
    FEATURES:
    - Chronological order (newest first)
    - Includes author info and timestamps
    - Edit status tracking
    
    PARAMS: page (default: 1)
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    comments = TaskQueryBuilder.get_task_comments(task)
    
    pagination = paginate_queryset(comments, page)
    
    return PaginatedCommentsSchema(
        results=[serialize_comment(comment) for comment in pagination['page_obj']],
        count=pagination['count'],
        has_next=pagination['has_next'],
        has_previous=pagination['has_previous']
    )


@router.get("/{int:task_id}/history", response=PaginatedHistorySchema)
def get_task_history(request, task_id: int, page: int = 1):
    """
    Get paginated task audit history (20 per page)
    
    TRACKS:
    - All task modifications and field changes
    - User actions and timestamps
    - Status transitions and assignments
    
    PARAMS: page (default: 1)
    """
    task = TaskQueryBuilder.get_task_with_relations(task_id)
    history = TaskQueryBuilder.get_task_history(task)
    
    pagination = paginate_queryset(history, page)
    
    return PaginatedHistorySchema(
        results=[serialize_history(item) for item in pagination['page_obj']],
        count=pagination['count'],
        has_next=pagination['has_next'],
        has_previous=pagination['has_previous']
    )