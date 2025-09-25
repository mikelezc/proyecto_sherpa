"""
Task Business Logic

Pure business logic, validations, and utilities for task operations.
Contains domain-specific calculations, validation rules, and business processes.
"""

from django.utils import timezone
from django.db import connection
from django.core.exceptions import ValidationError


def validate_task_due_date(task):
    """Validate that due date is not in the past for new tasks"""
    if task.due_date and task.due_date < timezone.now():
        if task.status in ['todo', 'pending']:
            raise ValidationError("Due date cannot be in the past for new tasks")


def validate_parent_task(task):
    """Validate that a task is not its own parent"""
    if task.parent_task == task:
        raise ValidationError("A task cannot be its own parent")


def validate_metadata(task):
    """Ensure metadata field is properly initialized"""
    if task.metadata is None:
        task.metadata = {}


def update_task_search_vector(task_id):
    """Update PostgreSQL full-text search vector for a task"""
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
    """Calculate task completion progress based on subtasks"""
    subtasks = task.subtasks.all()
    if not subtasks:
        return 100 if task.status in ['done', 'completed'] else 0
    
    completed_subtasks = subtasks.filter(status__in=['done', 'completed']).count()
    return (completed_subtasks / subtasks.count()) * 100


def is_task_overdue(task):
    """Check if a task is overdue based on due date and status"""
    return (
        task.due_date < timezone.now() and 
        task.status not in ['done', 'completed', 'cancelled']
    )


def check_and_update_overdue_status(task):
    """Update task's overdue status based on current date and status"""
    if task.due_date and task.due_date < timezone.now():
        if task.status not in ['done', 'cancelled']:
            task.is_overdue = True
    else:
        task.is_overdue = False


def get_task_changes(old_task, new_task):
    """Compare two task instances and return changes dictionary"""
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