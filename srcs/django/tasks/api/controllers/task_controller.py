"""
Task Management API Controllers
REST API controllers for task CRUD operations using Django Ninja
"""

from typing import List, Optional
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone
from ninja import Router
from tasks.models import Task, Tag, Team
from decimal import Decimal

from ..schemas import (
    TaskCreateSchema,
    TaskUpdateSchema, 
    TaskPatchSchema,
    TaskDetailSchema,
    TaskListSchema,
    PaginatedTasksSchema,
    TaskDeleteResponseSchema,
    UserMinimalSchema,
    TagSchema,
    TeamSchema
)

User = get_user_model()
router = Router()


def serialize_user_minimal(user):
    """Helper to serialize user to minimal schema"""
    return UserMinimalSchema(
        id=user.id,
        username=user.username,
        email=user.email
    )


def serialize_tag(tag):
    """Helper to serialize tag"""
    return TagSchema(
        id=tag.id,
        name=tag.name,
        color=tag.color
    )


def serialize_team(team):
    """Helper to serialize team"""
    if team:
        return TeamSchema(
            id=team.id,
            name=team.name
        )
    return None


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
        team=serialize_team(task.team),
        parent_task_id=task.parent_task.id if task.parent_task else None,
        metadata=task.metadata,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_archived=task.is_archived,
        is_overdue=task.is_past_due
    )


@router.get("/", response=PaginatedTasksSchema)
def list_tasks(
    request,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None,
    tag: Optional[str] = None,
    is_overdue: Optional[bool] = None
):
    """
    List tasks with filtering, search, and pagination
    
    Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search in title and description
    - status: Filter by status (todo, in_progress, review, done, cancelled)
    - priority: Filter by priority (low, medium, high, critical)
    - assigned_to: Filter by assigned user ID
    - created_by: Filter by creator user ID
    - tag: Filter by tag name
    - is_overdue: Filter by overdue status
    
    Returns:
    - 200: Paginated task list
    """
    # Limit page size
    page_size = min(page_size, 100)
    
    # Build queryset with optimizations
    queryset = Task.objects.select_related('created_by', 'team', 'parent_task').prefetch_related(
        'assigned_to',
        'tags'
    ).filter(is_archived=False)
    
    # Apply search filter
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Apply status filter
    if status:
        queryset = queryset.filter(status=status)
    
    # Apply priority filter
    if priority:
        queryset = queryset.filter(priority=priority)
    
    # Apply assigned_to filter
    if assigned_to:
        queryset = queryset.filter(assigned_to__id=assigned_to)
    
    # Apply created_by filter
    if created_by:
        queryset = queryset.filter(created_by__id=created_by)
    
    # Apply tag filter
    if tag:
        queryset = queryset.filter(tags__name__icontains=tag)
    
    # Apply overdue filter
    if is_overdue is not None:
        if is_overdue:
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['todo', 'in_progress', 'review']
            )
        else:
            queryset = queryset.exclude(
                due_date__lt=timezone.now(),
                status__in=['todo', 'in_progress', 'review']
            )
    
    # Order by priority and due date
    queryset = queryset.order_by('-priority', 'due_date', '-created_at')
    
    # Paginate
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize tasks
    tasks_data = [serialize_task_list(task) for task in page_obj]
    
    return PaginatedTasksSchema(
        count=paginator.count,
        next=None,  # Simplified for now
        previous=None,  # Simplified for now
        results=tasks_data
    )


@router.post("/", response=TaskDetailSchema)
def create_task(request, data: TaskCreateSchema):
    """
    Create a new task
    
    Parameters:
    - data: Task creation data
    
    Returns:
    - 201: Created task details
    """
    # For now, use first user as creator (in real app, get from JWT)
    creator = User.objects.filter(is_active=True).first()
    
    # Create the task
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
        estimated_hours=data.estimated_hours or Decimal('0'),
        created_by=creator,
        metadata=data.metadata if data.metadata else {}
    )
    task.save(force_insert=True)  # Skip full_clean() for now
    
    # Set relationships
    if data.assigned_to_ids:
        users = User.objects.filter(id__in=data.assigned_to_ids)
        task.assigned_to.set(users)
    
    if data.tag_ids:
        tags = Tag.objects.filter(id__in=data.tag_ids)
        task.tags.set(tags)
    
    if data.parent_task_id:
        try:
            parent = Task.objects.get(id=data.parent_task_id)
            task.parent_task = parent
            task.save()
        except Task.DoesNotExist:
            pass
    
    if data.team_id:
        try:
            team = Team.objects.get(id=data.team_id)
            task.team = team
            task.save()
        except Team.DoesNotExist:
            pass
    
    # Refresh to get relationships
    task.refresh_from_db()
    
    return serialize_task_detail(task)


@router.get("/{task_id}", response=TaskDetailSchema)
def get_task_detail(request, task_id: int):
    """
    Get task details by ID
    
    Parameters:
    - task_id: Task ID
    
    Returns:
    - 200: Task details
    """
    task = Task.objects.select_related('created_by', 'team', 'parent_task').prefetch_related(
        'assigned_to',
        'tags'
    ).get(id=task_id, is_archived=False)
    
    return serialize_task_detail(task)


@router.put("/{task_id}", response=TaskDetailSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    """
    Update task (full update)
    
    Parameters:
    - task_id: Task ID
    - data: Task update data
    
    Returns:
    - 200: Updated task details
    """
    task = Task.objects.get(id=task_id, is_archived=False)
    
    # Update fields if provided
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
    if data.priority is not None:
        task.priority = data.priority
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.estimated_hours is not None:
        task.estimated_hours = data.estimated_hours
    if data.actual_hours is not None:
        task.actual_hours = data.actual_hours
    if data.metadata is not None:
        task.metadata = data.metadata
    
    task.save()
    
    # Update relationships
    if data.assigned_to_ids is not None:
        if data.assigned_to_ids:
            users = User.objects.filter(id__in=data.assigned_to_ids)
            task.assigned_to.set(users)
        else:
            task.assigned_to.clear()
    
    if data.tag_ids is not None:
        if data.tag_ids:
            tags = Tag.objects.filter(id__in=data.tag_ids)
            task.tags.set(tags)
        else:
            task.tags.clear()
    
    # Refresh to get updated relationships
    task.refresh_from_db()
    
    return serialize_task_detail(task)


@router.patch("/{task_id}", response=TaskDetailSchema)
def patch_task(request, task_id: int, data: TaskPatchSchema):
    """
    Partial update task (PATCH)
    
    Parameters:
    - task_id: Task ID
    - data: Partial task update data
    
    Returns:
    - 200: Updated task details
    """
    task = Task.objects.get(id=task_id, is_archived=False)
    
    # Update only provided fields
    if data.status is not None:
        task.status = data.status
    if data.priority is not None:
        task.priority = data.priority
    if data.actual_hours is not None:
        task.actual_hours = data.actual_hours
    
    task.save()
    task.refresh_from_db()
    
    return serialize_task_detail(task)


@router.delete("/{task_id}", response=TaskDeleteResponseSchema)
def delete_task(request, task_id: int):
    """
    Delete task (soft delete by archiving)
    
    Parameters:
    - task_id: Task ID
    
    Returns:
    - 200: Deletion success confirmation
    """
    task = Task.objects.get(id=task_id, is_archived=False)
    
    # Soft delete by archiving
    task.is_archived = True
    task.save()
    
    return TaskDeleteResponseSchema(
        success=True,
        message=f"Task '{task.title}' has been successfully deleted"
    )
