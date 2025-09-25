"""
Task API Services


Contains complex business operations, validations, and data processing.
Separates business logic from HTTP concerns in controllers.
"""

from typing import List
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404

from tasks.models import Task, Tag, TaskAssignment, Comment, TaskHistory
from tasks.business import (
    validate_task_due_date,
    validate_parent_task, 
    validate_metadata,
    update_task_search_vector
)
from tasks.task_helpers import TaskSearchUtils

User = get_user_model()


class TaskService:
    """Service class for task-related business operations"""
    
    @staticmethod
    def create_task(user, data) -> Task:
        """Create a new task with assignments and tags"""
        with transaction.atomic():
            # Create the task
            task = Task.objects.create(
                title=data.title,
                description=data.description,
                status=data.status,
                priority=data.priority,
                due_date=data.due_date,
                estimated_hours=data.estimated_hours or Decimal('0'),
                created_by=user,
                team_id=data.team_id,
                parent_task_id=data.parent_task_id,
                metadata=data.metadata or {}
            )
            
            # Apply business validations
            validate_task_due_date(task)
            validate_parent_task(task)
            validate_metadata(task)
            
            # Handle assignments
            if data.assigned_to_ids:
                TaskService._create_assignments(task, data.assigned_to_ids, user)
            
            # Handle tags
            if data.tag_ids:
                TaskService._set_tags(task, data.tag_ids)
            
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
                value = getattr(data, field)
                if value is not None:
                    setattr(task, field, value)
            
            if data.metadata is not None:
                task.metadata = data.metadata
            
            # Apply business validations
            validate_task_due_date(task)
            validate_parent_task(task)
            validate_metadata(task)
            
            task.save()
            
            # Update assignments if provided
            if data.assigned_to_ids is not None:
                TaskService._update_assignments(task, data.assigned_to_ids, user)
            
            # Update tags if provided
            if data.tag_ids is not None:
                TaskService._set_tags(task, data.tag_ids)
            
            # Update search vector
            update_task_search_vector(task.id)
            
            return task
    
    @staticmethod
    def partial_update_task(task: Task, data) -> Task:
        """Partially update a task (PATCH operation)"""
        with transaction.atomic():
            # Update only provided fields
            for field in ['status', 'priority', 'actual_hours']:
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
        TaskService._create_assignments(task, user_ids, assigned_by)
    
    @staticmethod
    def _set_tags(task: Task, tag_ids: List[int]) -> None:
        """Helper to set task tags"""
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            task.tags.set(tags)
        else:
            task.tags.clear()

    @staticmethod
    def _update_search_vector(task: Task) -> None:
        """Helper to update task search vector using model utilities"""
        # Use both approaches for now - business logic and utilities
        update_task_search_vector(task.id)


class TaskQueryService:
    """Service class for task querying operations"""
    
    @staticmethod
    def get_task_with_relations(task_id: int) -> Task:
        """Get a task with all related data or raise Http404"""
        try:
            return Task.objects.select_related(
                'created_by', 'team', 'parent_task'
            ).prefetch_related(
                'assigned_to', 'tags'
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise Http404("Task not found")
    
    @staticmethod
    def get_task_assignments(task: Task):
        """Get all assignments for a task with related data"""
        return TaskAssignment.objects.filter(task=task).select_related('user', 'assigned_by')
    
    @staticmethod
    def get_task_comments(task: Task):
        """Get comments for a task ordered by creation date"""
        return Comment.objects.filter(task=task).select_related('author').order_by('-created_at')
    
    @staticmethod
    def get_task_history(task: Task):
        """Get history for a task ordered by timestamp"""
        return TaskHistory.objects.filter(task=task).select_related('user').order_by('-timestamp')