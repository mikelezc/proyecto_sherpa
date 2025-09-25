"""
Task Business Logic

Consolidated business logic, validations, utilities, and serializers.
Single place for all task-related operations, calculations, and data transformations.
"""

from django.utils import timezone
from django.db import connection
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.db import connection
from django.core.exceptions import ValidationError


def validate_task_due_date(task):
    if task.due_date and task.due_date < timezone.now():
        if task.status in ['todo', 'pending']:
            raise ValidationError("Due date cannot be in the past for new tasks")


def validate_parent_task(task):
    if task.parent_task == task:
        raise ValidationError("A task cannot be its own parent")


def validate_metadata(task):
    if task.metadata is None:
        task.metadata = {}


def update_task_search_vector(task_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tasks_task 
                SET search_vector = to_tsvector('english', 
                    COALESCE(title, '') || ' ' || COALESCE(description, '')
                ) 
                WHERE id = %s
                """,
                [task_id]
            )
    except Exception:
        # If PostgreSQL full-text search is not available, skip silently
        pass


def calculate_task_progress(task):
    subtasks = task.subtasks.all()
    if not subtasks:
        return 100 if task.status in ['done', 'completed'] else 0
    
    completed_subtasks = subtasks.filter(status__in=['done', 'completed']).count()
    return (completed_subtasks / subtasks.count()) * 100


def is_task_overdue(task):
    return (
        task.due_date < timezone.now() and 
        task.status not in ['done', 'completed', 'cancelled']
    )


def check_and_update_overdue_status(task):
    if task.due_date and task.due_date < timezone.now():
        if task.status not in ['done', 'cancelled']:
            task.is_overdue = True
    else:
        task.is_overdue = False


def get_task_changes(old_task, new_task):
    changes = {}
    
    if old_task.status != new_task.status:
        changes['old_status'] = old_task.status
        changes['new_status'] = new_task.status
        
    if old_task.title != new_task.title:
        changes['old_title'] = old_task.title
        changes['new_title'] = new_task.title
        
    if old_task.description != new_task.description:
        changes['description_changed'] = True
        
    return changes


# ============================
# SERIALIZATION HELPERS
# ============================
# Moved from duplicated controller files to eliminate redundancy

def serialize_user_minimal(user):
    """Helper to serialize user to minimal schema (moved from controllers)"""
    from .api.schemas import UserMinimalSchema
    return UserMinimalSchema(
        id=user.id,
        username=user.username,
        email=user.email
    )


def serialize_tag(tag):
    """Helper to serialize tag (moved from controllers)"""
    from .api.schemas import TagSchema
    return TagSchema(
        id=tag.id,
        name=tag.name,
        color=tag.color
    )


def serialize_team(team):
    """Helper to serialize team (moved from controllers)"""
    from .api.schemas import TeamSchema
    return TeamSchema(
        id=team.id,
        name=team.name
    )


def serialize_assignment(assignment):
    """Helper to serialize task assignment (moved from controllers)"""
    from .api.schemas import TaskAssignmentSchema
    return TaskAssignmentSchema(
        id=assignment.id,
        user=serialize_user_minimal(assignment.user),
        assigned_at=assignment.assigned_at,
        assigned_by=serialize_user_minimal(assignment.assigned_by),
        is_primary=assignment.is_primary
    )


def serialize_comment(comment):
    """Helper to serialize comment (moved from controllers)"""
    from .api.schemas import CommentSchema
    return CommentSchema(
        id=comment.id,
        content=comment.content,
        author=serialize_user_minimal(comment.author),
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_edited=comment.is_edited
    )