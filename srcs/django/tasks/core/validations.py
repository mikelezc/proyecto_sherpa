"""
Task Validation Utilities

Centralized business rules validation for task operations.
Contains all validation logic in a unified location.
"""

from django.utils import timezone
from django.core.exceptions import ValidationError


class TaskValidationUtils:
    """Validation utilities for Task models"""
    
    @staticmethod
    def validate_task_hierarchy(task):
        """Validate task parent-child relationships"""
        # Check if parent_task_id is None or 0 (no parent)
        if not task.parent_task_id:
            return True
            
        # Check for circular dependencies
        try:
            current = task.parent_task
        except task.__class__.DoesNotExist:
            raise ValueError(f"Parent task with ID {task.parent_task_id} does not exist")
            
        visited = {task.id}
        
        while current:
            if current.id in visited:
                raise ValueError("Circular dependency detected in task hierarchy")
            visited.add(current.id)
            current = current.parent_task
            
        return True
    
    @staticmethod
    def validate_due_date(task):
        """Validate task due date (enhanced validation)"""
        # Validate due date exists and is not in the past for new tasks
        if task.due_date:
            if task.due_date < timezone.now() and task.status in ['todo', 'pending']:
                raise ValidationError("Due date cannot be in the past for new tasks")
            
            # Validate due date is after creation date (if task exists)
            if task.created_at and task.due_date <= task.created_at:
                raise ValueError("Due date must be after creation date")
        
        return True
    
    @staticmethod
    def validate_hours(task):
        """Validate task hour fields"""
        if task.estimated_hours and task.estimated_hours < 0:
            raise ValueError("Estimated hours cannot be negative")
            
        if task.actual_hours and task.actual_hours < 0:
            raise ValueError("Actual hours cannot be negative")
            
        return True
    
    @staticmethod
    def validate_parent_task(task):
        """Validate that a task is not its own parent"""
        if task.parent_task == task:
            raise ValidationError("A task cannot be its own parent")
        return True
    
    @staticmethod
    def validate_metadata(task):
        """Ensure metadata field is properly initialized"""
        if task.metadata is None:
            task.metadata = {}
        return True