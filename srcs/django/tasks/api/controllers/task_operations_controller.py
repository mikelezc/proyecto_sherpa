"""
Task Operations API Controllers
Advanced task operations: assign, comments, history
"""

from typing import List, Optional
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.utils import timezone
from ninja import Router
from tasks.models import Task, TaskAssignment, Comment, TaskHistory
from decimal import Decimal

from ..schemas import (
    TaskAssignSchema,
    TaskAssignResponseSchema,
    TaskAssignmentSchema,
    CommentCreateSchema,
    CommentSchema,
    PaginatedCommentsSchema,
    TaskHistorySchema,
    PaginatedHistorySchema,
    UserMinimalSchema,
    TaskErrorSchema
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


def serialize_assignment(assignment):
    """Helper to serialize task assignment"""
    return TaskAssignmentSchema(
        id=assignment.id,
        user=serialize_user_minimal(assignment.user),
        assigned_at=assignment.assigned_at,
        assigned_by=serialize_user_minimal(assignment.assigned_by),
        is_primary=assignment.is_primary
    )


def serialize_comment(comment):
    """Helper to serialize comment"""
    return CommentSchema(
        id=comment.id,
        author=serialize_user_minimal(comment.author),
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_edited=comment.is_edited
    )


def serialize_history(history):
    """Helper to serialize task history"""
    return TaskHistorySchema(
        id=history.id,
        user=serialize_user_minimal(history.user),
        action=history.action,
        changes=history.changes,
        timestamp=history.timestamp
    )


def create_history_entry(task, user, action, changes=None):
    """Helper to create task history entry"""
    TaskHistory.objects.create(
        task=task,
        user=user,
        action=action,
        changes=changes or {}
    )


@router.post("/{task_id}/assign/", response=TaskAssignResponseSchema)
def assign_task(request, task_id: int, data: TaskAssignSchema):
    """
    Assign users to a task
    
    Parameters:
    - task_id: Task ID
    - data: Assignment data with user IDs
    
    Returns:
    - 200: Assignment success with details
    """
    # Get the task
    task = Task.objects.get(id=task_id, is_archived=False)
    
    # Get current user (for now, use first user)
    assigner = User.objects.filter(is_active=True).first()
    
    # Get users to assign
    users_to_assign = User.objects.filter(id__in=data.user_ids, is_active=True)
    
    if not users_to_assign.exists():
        return TaskAssignResponseSchema(
            success=False,
            message="No valid users found to assign",
            assignments=[]
        )
    
    assignments = []
    assigned_users = []
    
    # Create assignments
    for user in users_to_assign:
        # Check if user is already assigned
        existing_assignment = TaskAssignment.objects.filter(task=task, user=user).first()
        
        if not existing_assignment:
            assignment = TaskAssignment.objects.create(
                task=task,
                user=user,
                assigned_by=assigner,
                is_primary=data.is_primary and len(data.user_ids) == 1  # Only primary if single assignment
            )
            assignments.append(serialize_assignment(assignment))
            assigned_users.append(user.username)
            
            # Create history entry
            create_history_entry(
                task=task,
                user=assigner,
                action='assigned',
                changes={
                    'assigned_user': user.username,
                    'assigned_user_id': user.id,
                    'is_primary': assignment.is_primary
                }
            )
        else:
            # User already assigned, add to response
            assignments.append(serialize_assignment(existing_assignment))
    
    message = f"Successfully assigned {len(assigned_users)} users to task"
    if assigned_users:
        message += f": {', '.join(assigned_users)}"
    
    return TaskAssignResponseSchema(
        success=True,
        message=message,
        assignments=assignments
    )


@router.post("/{task_id}/comments/", response=CommentSchema)
def create_comment(request, task_id: int, data: CommentCreateSchema):
    """
    Add a comment to a task
    
    Parameters:
    - task_id: Task ID
    - data: Comment content
    
    Returns:
    - 201: Created comment details
    """
    # Get the task
    task = Task.objects.get(id=task_id, is_archived=False)
    
    # Get current user (for now, use first user)
    author = User.objects.filter(is_active=True).first()
    
    # Create the comment
    comment = Comment.objects.create(
        task=task,
        author=author,
        content=data.content
    )
    
    # Create history entry
    create_history_entry(
        task=task,
        user=author,
        action='updated',
        changes={
            'comment_added': True,
            'comment_id': comment.id,
            'comment_content': data.content[:100] + "..." if len(data.content) > 100 else data.content
        }
    )
    
    return serialize_comment(comment)


@router.get("/{task_id}/comments/", response=PaginatedCommentsSchema)
def list_comments(
    request, 
    task_id: int,
    page: int = 1,
    page_size: int = 20
):
    """
    Get comments for a task
    
    Parameters:
    - task_id: Task ID
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    
    Returns:
    - 200: Paginated comments list
    """
    # Get the task
    task = Task.objects.get(id=task_id, is_archived=False)
    
    # Limit page size
    page_size = min(page_size, 100)
    
    # Get comments with author information
    queryset = Comment.objects.select_related('author').filter(task=task)
    
    # Paginate
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize comments
    comments_data = [serialize_comment(comment) for comment in page_obj]
    
    return PaginatedCommentsSchema(
        count=paginator.count,
        next=None,  # Simplified for now
        previous=None,  # Simplified for now
        results=comments_data
    )


@router.get("/{task_id}/history/", response=PaginatedHistorySchema)
def list_history(
    request,
    task_id: int, 
    page: int = 1,
    page_size: int = 20,
    action: Optional[str] = None
):
    """
    Get history for a task
    
    Parameters:
    - task_id: Task ID
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - action: Filter by action type (created, updated, assigned, etc.)
    
    Returns:
    - 200: Paginated history list
    """
    # Get the task
    task = Task.objects.get(id=task_id, is_archived=False)
    
    # Limit page size
    page_size = min(page_size, 100)
    
    # Get history with user information
    queryset = TaskHistory.objects.select_related('user').filter(task=task)
    
    # Apply action filter if provided
    if action:
        queryset = queryset.filter(action=action)
    
    # Paginate
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize history
    history_data = [serialize_history(history) for history in page_obj]
    
    return PaginatedHistorySchema(
        count=paginator.count,
        next=None,  # Simplified for now
        previous=None,  # Simplified for now
        results=history_data
    )
