"""
Task Form Adapter - WEB form processing and pagination

Contains web-specific logic, pagination, and form processing.
Bridges between WEB views and core CRUD operations.
Handles form-to-service data transformation.
"""

from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .task_query_builder import TaskQueryBuilder
from .task_crud_operations import TaskCrudOperations
from .form_adapters import FormDataAdapter

User = get_user_model()


class TaskFormAdapter:
    """Service class for WEB form processing and task operations"""
    
    @staticmethod
    def get_filtered_tasks_for_user(user, filter_params, page=1, page_size=10):
        """Get filtered and paginated tasks for web interface"""
        # Add user context to filters
        enhanced_filters = dict(filter_params) if filter_params else {}
        enhanced_filters['user'] = user
        
        # Use unified query builder directly
        queryset = TaskQueryBuilder.build_from_params(**enhanced_filters)
        
        # Apply pagination
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'tasks': page_obj,
            'paginator': paginator,
            'page_obj': page_obj
        }
    
    @staticmethod
    def get_task_detail_for_web(task_id, user):
        """Get task detail with all related data for web view"""
        # Direct query operations without unnecessary service layer
        from ..models import Task, TaskAssignment, Comment, TaskHistory
        from django.http import Http404
        
        try:
            task = Task.objects.select_related(
                'created_by', 'team', 'parent_task'
            ).prefetch_related(
                'assigned_to', 'tags'
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise Http404("Task not found")
        
        return {
            'task': task,
            'assignments': TaskAssignment.objects.filter(task=task).select_related('user', 'assigned_by'),
            'comments': Comment.objects.filter(task=task).select_related('author').order_by('-created_at'),
            'history': TaskHistory.objects.filter(task=task).select_related('user').order_by('-timestamp')
        }
    
    @staticmethod
    def create_task_from_form(form, user):
        """Create task from web form data"""
        # Use the centralized form adapter
        form_data = FormDataAdapter.from_form(form)
        return TaskCrudOperations.create_task(user, form_data)
    
    @staticmethod
    def update_task_from_form(task, form, user):
        """Update task from web form data"""
        # Use the centralized form adapter
        form_data = FormDataAdapter.from_form(form)
        return TaskCrudOperations.update_task(task, user, form_data)
    
    @staticmethod
    def get_dashboard_stats(user):
        """Get dashboard statistics for user"""
        base_query = TaskQueryBuilder.build_from_params(user=user)
        
        stats = {
            'total_tasks': base_query.count(),
            'todo_tasks': base_query.filter(status='todo').count(),
            'in_progress_tasks': base_query.filter(status='in_progress').count(),
            'done_tasks': base_query.filter(status__in=['done', 'completed']).count(),
            'high_priority_tasks': base_query.filter(priority__in=['high', 'critical']).count()
        }
        
        return stats