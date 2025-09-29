"""
Task CRUD Operations - Core task business operations

Contains task creation, update, delete, and management operations.
Provides clean separation between data operations and query logic.
Shared between API and WEB interfaces.
"""

from typing import List
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction

from ..models import Task, Tag, TaskAssignment, Comment
from ..core.business import (
    validate_task_due_date,
    validate_parent_task, 
    validate_metadata,
    update_task_search_vector
)

User = get_user_model()


class TaskCrudOperations:
    """Service class for task-related business operations"""
    
    @staticmethod
    def create_task(user, data) -> Task:
        """Create a new task with assignments and tags"""
        from django.utils import timezone
        from datetime import timedelta
        
        with transaction.atomic():
            # Handle parent_task_id: convert 0 to None
            parent_task_id = getattr(data, 'parent_task_id', None)
            if parent_task_id == 0:
                parent_task_id = None
                
            # Handle team_id: convert 0 to None  
            team_id = getattr(data, 'team_id', None)
            if team_id == 0:
                team_id = None
            
            # Ensure due_date is in the future
            due_date = data.due_date
            current_time = timezone.now()
            if due_date <= current_time:
                # If due_date is in the past, set it to 1 week from now
                due_date = current_time + timedelta(days=7)
            
            # Create the task
            task = Task.objects.create(
                title=data.title,
                description=data.description,
                status=data.status,
                priority=data.priority,
                due_date=due_date,
                estimated_hours=data.estimated_hours or Decimal('0'),
                created_by=user,
                team_id=team_id,
                parent_task_id=parent_task_id,
                metadata=getattr(data, 'metadata', {}) or {}
            )
            
            # Apply business validations
            validate_task_due_date(task)
            validate_parent_task(task)
            validate_metadata(task)
            
            # Handle assignments
            if hasattr(data, 'assigned_to_ids') and data.assigned_to_ids:
                TaskCrudOperations._create_assignments(task, data.assigned_to_ids, user)
            
            # Handle tags
            if hasattr(data, 'tag_ids') and data.tag_ids:
                TaskCrudOperations._set_tags(task, data.tag_ids)
            
            # Update search vector
            update_task_search_vector(task.id)
            
            return task
    
    @staticmethod
    def update_task(task: Task, user, data) -> Task:
        """Update a task with all related data"""
        with transaction.atomic():
            # Update basic fields
            for field in ['title', 'description', 'status', 'priority', 'due_date', 
                         'estimated_hours', 'actual_hours']:
                if hasattr(data, field):
                    value = getattr(data, field)
                    if value is not None:
                        setattr(task, field, value)
            
            if hasattr(data, 'metadata') and data.metadata is not None:
                task.metadata = data.metadata
            
            # Apply business validations
            validate_task_due_date(task)
            validate_parent_task(task)
            validate_metadata(task)
            
            task.save()
            
            # Update assignments if provided
            if hasattr(data, 'assigned_to_ids') and data.assigned_to_ids is not None:
                TaskCrudOperations._update_assignments(task, data.assigned_to_ids, user)
            
            # Update tags if provided
            if hasattr(data, 'tag_ids') and data.tag_ids is not None:
                TaskCrudOperations._set_tags(task, data.tag_ids)
            
            # Update search vector
            update_task_search_vector(task.id)
            
            return task
    
    @staticmethod
    def partial_update_task(task: Task, data) -> Task:
        """Partially update a task (PATCH operation)"""
        with transaction.atomic():
            # Update only provided fields
            for field in ['status', 'priority', 'actual_hours']:
                if hasattr(data, field):
                    value = getattr(data, field)
                    if value is not None:
                        setattr(task, field, value)
            
            # Apply business validations
            validate_task_due_date(task)
            
            task.save()
            
            # Update search vector
            update_task_search_vector(task.id)
            
            return task
    
    @staticmethod
    def archive_task(task: Task) -> Task:
        """Archive a task (soft delete)"""
        task.is_archived = True
        task.save()
        return task
    
    @staticmethod
    def assign_users_to_task(task: Task, user_ids: List[int], assigned_by, is_primary: bool = False) -> List[TaskAssignment]:
        """Assign multiple users to a task"""
        with transaction.atomic():
            users = User.objects.filter(id__in=user_ids)
            assignments_created = []
            
            for user in users:
                assignment, created = TaskAssignment.objects.get_or_create(
                    task=task,
                    user=user,
                    defaults={
                        'assigned_by': assigned_by,
                        'is_primary': is_primary and user == users.first()
                    }
                )
                if created:
                    assignments_created.append(assignment)
            
            return assignments_created
    
    @staticmethod
    def unassign_user_from_task(task_id: int, user_id: int) -> bool:
        """Remove a user assignment from a task"""
        try:
            assignment = TaskAssignment.objects.get(task_id=task_id, user_id=user_id)
            assignment.delete()
            return True
        except TaskAssignment.DoesNotExist:
            return False
    
    @staticmethod
    def create_comment(task: Task, user, content: str) -> Comment:
        """Create a comment on a task"""
        comment = Comment.objects.create(
            task=task,
            author=user,
            content=content
        )
        return comment
    
    @staticmethod
    def _create_assignments(task: Task, user_ids: List[int], assigned_by) -> None:
        """Helper to create task assignments"""
        if not user_ids:
            return
            
        users = User.objects.filter(id__in=user_ids)
        for i, user in enumerate(users):
            TaskAssignment.objects.create(
                task=task,
                user=user,
                assigned_by=assigned_by,
                is_primary=(i == 0)  # First user is primary
            )
    
    @staticmethod
    def _update_assignments(task: Task, user_ids: List[int], assigned_by) -> None:
        """Helper to update task assignments"""
        # Clear existing assignments
        TaskAssignment.objects.filter(task=task).delete()
        
        # Create new assignments
        TaskCrudOperations._create_assignments(task, user_ids, assigned_by)
    
    @staticmethod
    def _set_tags(task: Task, tag_ids: List[int]) -> None:
        """Helper to set task tags"""
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            task.tags.set(tags)
        else:
            task.tags.clear()