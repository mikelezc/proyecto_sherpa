"""
Task Helper Utilities - Business Logic Layer

This module provides centralized utility classes for task-related operations,
implementing core business logic that serves the model layer through mixins.

ARCHITECTURE PATTERN:
task_helpers.py → mixins.py → models.py → rest of application

UTILITY CLASSES:
- TaskModelUtils: Calculations (progress, hours, deadlines)
- TaskValidationUtils: Business rules validation  
- TaskMetadataUtils: Metadata management operations

PURPOSE: Keep models clean by extracting complex business logic into
reusable, testable utility functions that are consumed via mixins.
"""

from ..constants import TASK_STATUS_PROGRESS, COMPLETED_STATUSES, DEFAULT_TASK_METADATA
from django.utils import timezone


class TaskModelUtils:
    """Static utilities for Task model operations"""
    
    @staticmethod
    def is_task_overdue(task):
        """Check if a task is past its due date"""
        if not task.due_date:
            return False
        return timezone.now() > task.due_date and task.status not in ['done', 'completed', 'cancelled']
    
    @staticmethod
    def calculate_progress_percentage(task):
        """Calculate task progress based on subtasks completion"""
        subtasks = task.subtasks.filter(is_archived=False)
        if not subtasks.exists():
            # No subtasks, calculate based on status using constants
            return TASK_STATUS_PROGRESS.get(task.status, 0)
        
        # Calculate based on subtasks
        total_subtasks = subtasks.count()
        completed_subtasks = subtasks.filter(
            status__in=COMPLETED_STATUSES
        ).count()
        
        if total_subtasks == 0:
            return 0
            
        return int((completed_subtasks / total_subtasks) * 100)


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
        """Validate task due date"""
        if task.due_date and task.created_at and task.due_date <= task.created_at:
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


class TaskMetadataUtils:
    """Utilities for task metadata operations"""
    
    @staticmethod
    def ensure_default_metadata(task):
        """Ensure task has default metadata structure"""
        if not task.metadata:
            task.metadata = DEFAULT_TASK_METADATA.copy()
            return
            
        # Ensure required keys exist by merging with defaults
        for key, default_value in DEFAULT_TASK_METADATA.items():
            if key not in task.metadata:
                if isinstance(default_value, dict):
                    task.metadata[key] = default_value.copy()
                elif isinstance(default_value, list):
                    task.metadata[key] = default_value.copy()
                else:
                    task.metadata[key] = default_value