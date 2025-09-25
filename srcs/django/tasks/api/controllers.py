"""
Task Management API Controllers
Consolidated REST API controllers for all task operations using Django Ninja
"""

from typing import Optional
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from ninja import Router
from tasks.models import Task, Tag, TaskAssignment, Comment, TaskHistory
from decimal import Decimal
from tasks.business import (
    serialize_user_minimal, 
    serialize_tag, 
    serialize_team, 
    serialize_assignment,
    serialize_comment
)

from .schemas import (
    # Task schemas
    TaskCreateSchema,
    TaskUpdateSchema, 
    TaskPatchSchema,
    TaskDetailSchema,
    TaskListSchema,
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
    UserMinimalSchema,
    TagSchema,
    TeamSchema,
    TaskErrorSchema
)

User = get_user_model()
router = Router()


def serialize_task_list(task):
    """Helper to serialize task for list view"""
    return TaskListSchema(
        id=task.id,
        title=task.title,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        created_by=serialize_user_minimal(task.created_by),
        assigned_to=[serialize_user_minimal(user) for user in task.assigned_to.all()],
        tags=[serialize_tag(tag) for tag in task.tags.all()],
        created_at=task.created_at,
        is_overdue=task.is_past_due
    )


def serialize_task_detail(task):
    """Helper to serialize task for detail view"""
    return TaskDetailSchema(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_by=serialize_user_minimal(task.created_by),
        assigned_to=[serialize_user_minimal(user) for user in task.assigned_to.all()],
        tags=[serialize_tag(tag) for tag in task.tags.all()],
        team=serialize_team(task.team) if task.team else None,
        parent_task_id=task.parent_task.id if task.parent_task else None,
        metadata=task.metadata,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_archived=task.is_archived,
        is_overdue=task.is_past_due
    )


# ============================
# TASK CRUD OPERATIONS
# ============================

@router.get("/", response=PaginatedTasksSchema)
def list_tasks(request, page: int = 1, status: Optional[str] = None, priority: Optional[str] = None, 
               assigned_to_me: bool = False, search: Optional[str] = None):
    """Get paginated list of tasks with optional filtering"""
    
    queryset = Task.objects.filter(is_archived=False).select_related('created_by', 'team').prefetch_related('assigned_to', 'tags')
    
    # Apply filters
    if status:
        queryset = queryset.filter(status=status)
    if priority:
        queryset = queryset.filter(priority=priority)
    if assigned_to_me:
        queryset = queryset.filter(assigned_to=request.user)
    if search:
        # Use the search functionality
        queryset = Task.search_tasks(search)
    
    # Pagination
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(page)
    
    return PaginatedTasksSchema(
        results=[serialize_task_list(task) for task in page_obj],
        count=paginator.count,
        page=page,
        num_pages=paginator.num_pages,
        has_next=page_obj.has_next(),
        has_previous=page_obj.has_previous()
    )


@router.post("/", response=TaskDetailSchema)
def create_task(request, data: TaskCreateSchema):
    """Create a new task"""
    # Create the task
    task = Task.objects.create(
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
        estimated_hours=data.estimated_hours or Decimal('0'),
        created_by=request.user,
        team_id=data.team_id,
        parent_task_id=data.parent_task_id,
        metadata=data.metadata
    )
    
    # Set assigned users
    if data.assigned_to_ids:
        users = User.objects.filter(id__in=data.assigned_to_ids)
        for user in users:
            TaskAssignment.objects.create(
                task=task,
                user=user,
                assigned_by=request.user,
                is_primary=(user == users.first())
            )
    
    # Set tags
    if data.tag_ids:
        tags = Tag.objects.filter(id__in=data.tag_ids)
        task.tags.set(tags)
    
    return serialize_task_detail(task)


@router.get("/{int:task_id}", response=TaskDetailSchema)
def get_task(request, task_id: int):
    """Get a specific task by ID"""
    try:
        task = Task.objects.select_related('created_by', 'team', 'parent_task').prefetch_related('assigned_to', 'tags').get(id=task_id)
        return serialize_task_detail(task)
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)


@router.put("/{int:task_id}", response=TaskDetailSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    """Update a task completely"""
    try:
        task = Task.objects.get(id=task_id)
        
        # Update basic fields
        for field in ['title', 'description', 'status', 'priority', 'due_date', 'estimated_hours', 'actual_hours']:
            value = getattr(data, field)
            if value is not None:
                setattr(task, field, value)
        
        if data.metadata is not None:
            task.metadata = data.metadata
            
        task.save()
        
        # Update assigned users
        if data.assigned_to_ids is not None:
            # Clear existing assignments
            TaskAssignment.objects.filter(task=task).delete()
            # Add new assignments
            users = User.objects.filter(id__in=data.assigned_to_ids)
            for user in users:
                TaskAssignment.objects.create(
                    task=task,
                    user=user,
                    assigned_by=request.user,
                    is_primary=(user == users.first())
                )
        
        # Update tags
        if data.tag_ids is not None:
            tags = Tag.objects.filter(id__in=data.tag_ids)
            task.tags.set(tags)
        
        return serialize_task_detail(task)
        
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)


@router.patch("/{int:task_id}", response=TaskDetailSchema)
def partial_update_task(request, task_id: int, data: TaskPatchSchema):
    """Partially update a task (PATCH)"""
    try:
        task = Task.objects.get(id=task_id)
        
        # Update only provided fields
        for field in ['status', 'priority', 'actual_hours']:
            value = getattr(data, field)
            if value is not None:
                setattr(task, field, value)
        
        task.save()
        return serialize_task_detail(task)
        
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)


@router.delete("/{int:task_id}", response=TaskDeleteResponseSchema)
def delete_task(request, task_id: int):
    """Delete a task (soft delete)"""
    try:
        task = Task.objects.get(id=task_id)
        task.is_archived = True
        task.save()
        return TaskDeleteResponseSchema(success=True, message="Task archived successfully")
        
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)


# ============================
# TASK OPERATIONS
# ============================

@router.post("/{int:task_id}/assign", response=TaskAssignResponseSchema)
def assign_task(request, task_id: int, data: TaskAssignSchema):
    """Assign users to a task"""
    try:
        task = Task.objects.get(id=task_id)
        users = User.objects.filter(id__in=data.user_ids)
        
        assignments_created = []
        for user in users:
            assignment, created = TaskAssignment.objects.get_or_create(
                task=task,
                user=user,
                defaults={
                    'assigned_by': request.user,
                    'is_primary': data.is_primary and user == users.first()
                }
            )
            if created:
                assignments_created.append(serialize_assignment(assignment))
        
        return TaskAssignResponseSchema(
            success=True,
            message=f"Task assigned to {len(assignments_created)} users",
            assignments=assignments_created
        )
        
    except Task.DoesNotExist:
        return router.create_response(
            request, 
            TaskErrorSchema(success=False, error="Task not found"), 
            status=404
        )


@router.delete("/{int:task_id}/assign/{int:user_id}")
def unassign_task(request, task_id: int, user_id: int):
    """Remove a user assignment from a task"""
    try:
        assignment = TaskAssignment.objects.get(task_id=task_id, user_id=user_id)
        assignment.delete()
        return {"success": True, "message": "User unassigned successfully"}
        
    except TaskAssignment.DoesNotExist:
        return router.create_response(request, {"error": "Assignment not found"}, status=404)


@router.get("/{int:task_id}/assignments", response=list[TaskAssignmentSchema])
def get_task_assignments(request, task_id: int):
    """Get all assignments for a task"""
    try:
        task = Task.objects.get(id=task_id)
        assignments = TaskAssignment.objects.filter(task=task).select_related('user', 'assigned_by')
        return [serialize_assignment(assignment) for assignment in assignments]
        
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)


@router.post("/{int:task_id}/comments", response=CommentSchema)
def create_comment(request, task_id: int, data: CommentCreateSchema):
    """Add a comment to a task"""
    try:
        task = Task.objects.get(id=task_id)
        comment = Comment.objects.create(
            task=task,
            author=request.user,
            content=data.content
        )
        return serialize_comment(comment)
        
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)


@router.get("/{int:task_id}/comments", response=PaginatedCommentsSchema)
def get_task_comments(request, task_id: int, page: int = 1):
    """Get paginated comments for a task"""
    try:
        task = Task.objects.get(id=task_id)
        comments = Comment.objects.filter(task=task).select_related('author').order_by('-created_at')
        
        paginator = Paginator(comments, 20)
        page_obj = paginator.get_page(page)
        
        return PaginatedCommentsSchema(
            results=[serialize_comment(comment) for comment in page_obj],
            count=paginator.count,
            page=page,
            num_pages=paginator.num_pages,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous()
        )
        
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)


@router.get("/{int:task_id}/history", response=PaginatedHistorySchema)
def get_task_history(request, task_id: int, page: int = 1):
    """Get paginated history for a task"""
    try:
        task = Task.objects.get(id=task_id)
        history = TaskHistory.objects.filter(task=task).select_related('user').order_by('-timestamp')
        
        paginator = Paginator(history, 20)
        page_obj = paginator.get_page(page)
        
        def serialize_history(history_item):
            return TaskHistorySchema(
                id=history_item.id,
                action=history_item.action,
                changes=history_item.changes,
                timestamp=history_item.timestamp,
                user=serialize_user_minimal(history_item.user)
            )
        
        return PaginatedHistorySchema(
            results=[serialize_history(item) for item in page_obj],
            count=paginator.count,
            page=page,
            num_pages=paginator.num_pages,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous()
        )
        
    except Task.DoesNotExist:
        return router.create_response(request, {"detail": "Task not found"}, status=404)