"""
Task Management API Controllers

HTTP request/response handlers for task operations.
"""

from typing import Optional
from django.core.paginator import Paginator
from ninja import Router

from .services import TaskService, TaskQueryService
from .filters import TaskFilter
from .serializers import (
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
    """Get paginated list of tasks with optional filtering"""
    
    # Use the filter service to build the queryset
    filter_params = {
        'status': status,
        'priority': priority,
        'assigned_to_me': assigned_to_me,
        'user': request.user,
        'search': search
    }
    
    queryset = TaskFilter.build_from_params(**filter_params)
    
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
    """Create a new task"""
    task = TaskService.create_task(request.user, data)
    return serialize_task_detail(task)


@router.get("/tasks/{task_id}", response=TaskDetailSchema, tags=["tasks"])
def get_task_by_id(request, task_id: int):
    """Get a specific task by ID"""
    task = TaskQueryService.get_task_with_relations(task_id)
    return serialize_task_detail(task)


@router.put("/{int:task_id}", response=TaskDetailSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    """Update a task completely"""
    task = TaskQueryService.get_task_with_relations(task_id)
    updated_task = TaskService.update_task(task, request.user, data)
    return serialize_task_detail(updated_task)


@router.patch("/{int:task_id}", response=TaskDetailSchema)
def partial_update_task(request, task_id: int, data: TaskPatchSchema):
    """Partially update a task (PATCH)"""
    task = TaskQueryService.get_task_with_relations(task_id)
    updated_task = TaskService.partial_update_task(task, data)
    return serialize_task_detail(updated_task)


@router.delete("/{int:task_id}", response=TaskDeleteResponseSchema)
def delete_task(request, task_id: int):
    """Delete a task (soft delete)"""
    task = TaskQueryService.get_task_with_relations(task_id)
    TaskService.archive_task(task)
    return TaskDeleteResponseSchema(success=True, message="Task archived successfully")


# ============================
# TASK OPERATIONS
# ============================

@router.post("/{int:task_id}/assign", response=TaskAssignResponseSchema)
def assign_task(request, task_id: int, data: TaskAssignSchema):
    """Assign users to a task"""
    try:
        task = TaskQueryService.get_task_with_relations(task_id)
        assignments = TaskService.assign_users_to_task(
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
    """Remove a user assignment from a task"""
    success = TaskService.unassign_user_from_task(task_id, user_id)
    
    if success:
        return {"success": True, "message": "User unassigned successfully"}
    else:
        return {"error": "Assignment not found"}


@router.get("/{int:task_id}/assignments", response=list[TaskAssignmentSchema])
def get_task_assignments(request, task_id: int):
    """Get all assignments for a task"""
    task = TaskQueryService.get_task_with_relations(task_id)
    assignments = TaskQueryService.get_task_assignments(task)
    return [serialize_assignment(assignment) for assignment in assignments]


@router.post("/{int:task_id}/comments", response=CommentSchema)
def create_comment(request, task_id: int, data: CommentCreateSchema):
    """Add a comment to a task"""
    task = TaskQueryService.get_task_with_relations(task_id)
    comment = TaskService.create_comment(task, request.user, data.content)
    return serialize_comment(comment)


@router.get("/{int:task_id}/comments", response=PaginatedCommentsSchema)
def get_task_comments(request, task_id: int, page: int = 1):
    """Get paginated comments for a task"""
    task = TaskQueryService.get_task_with_relations(task_id)
    comments = TaskQueryService.get_task_comments(task)
    
    pagination = paginate_queryset(comments, page)
    
    return PaginatedCommentsSchema(
        results=[serialize_comment(comment) for comment in pagination['page_obj']],
        count=pagination['count'],
        has_next=pagination['has_next'],
        has_previous=pagination['has_previous']
    )


@router.get("/{int:task_id}/history", response=PaginatedHistorySchema)
def get_task_history(request, task_id: int, page: int = 1):
    """Get paginated history for a task"""
    task = TaskQueryService.get_task_with_relations(task_id)
    history = TaskQueryService.get_task_history(task)
    
    pagination = paginate_queryset(history, page)
    
    return PaginatedHistorySchema(
        results=[serialize_history(item) for item in pagination['page_obj']],
        count=pagination['count'],
        has_next=pagination['has_next'],
        has_previous=pagination['has_previous']
    )