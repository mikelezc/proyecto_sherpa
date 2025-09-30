"""
Task Calculation Utilities

Pure calculation functions for task metrics, progress, and business analytics.
Contains all computational logic without side effects.
"""

from django.utils import timezone
from ..constants import TASK_STATUS_PROGRESS, COMPLETED_STATUSES


class TaskCalculationUtils:
    """Calculation utilities for Task models"""
    
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
    
    @staticmethod
    def check_and_update_overdue_status(task):
        """Update task's overdue status based on current date and status"""
        if task.due_date and task.due_date < timezone.now():
            if task.status not in ['done', 'cancelled']:
                task.is_overdue = True
        else:
            task.is_overdue = False
        return task.is_overdue