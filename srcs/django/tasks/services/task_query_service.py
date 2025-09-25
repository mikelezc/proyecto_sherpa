"""
Task Query Service - Query and retrieval operations

Contains optimized queries for task retrieval and filtering.
Shared between API and WEB interfaces.
"""

from django.http import Http404

from ..models import Task, TaskAssignment, Comment, TaskHistory
from .task_filters import TaskFilter


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
    
    @staticmethod
    def build_filtered_query(filters=None):
        """Build a filtered queryset - DELEGATES to unified TaskFilter"""
        # Use the advanced filtering system
        return TaskFilter.build_from_params(**(filters or {}))