"""
Task Web Service - WEB-specific operations

Contains web-specific logic, pagination, and form processing.
Bridges between WEB views and core services.
"""

from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .task_query_service import TaskQueryService
from .task_service import TaskService

User = get_user_model()


class TaskWebService:
    """Service class for WEB-specific task operations"""
    
    @staticmethod
    def get_filtered_tasks_for_user(user, filter_params, page=1, page_size=10):
        """Get filtered and paginated tasks for web interface"""
        # Add user context to filters
        enhanced_filters = dict(filter_params) if filter_params else {}
        enhanced_filters['user'] = user
        
        # Use unified query service
        queryset = TaskQueryService.build_filtered_query(enhanced_filters)
        
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
        task = TaskQueryService.get_task_with_relations(task_id)
        
        return {
            'task': task,
            'assignments': TaskQueryService.get_task_assignments(task),
            'comments': TaskQueryService.get_task_comments(task),
            'history': TaskQueryService.get_task_history(task)
        }
    
    @staticmethod
    def create_task_from_form(form, user):
        """Create task from web form data"""
        # Convert form data to service-compatible format
        class FormData:
            def __init__(self, cleaned_data):
                for key, value in cleaned_data.items():
                    setattr(self, key, value)
                # Handle many-to-many fields
                if 'assigned_to' in cleaned_data:
                    self.assigned_to_ids = [user.id for user in cleaned_data['assigned_to']]
                if 'tags' in cleaned_data:
                    self.tag_ids = [tag.id for tag in cleaned_data['tags']]
                # Handle foreign key fields that need _id suffix
                if 'team' in cleaned_data and cleaned_data['team']:
                    self.team_id = cleaned_data['team'].id
                if 'parent_task' in cleaned_data and cleaned_data['parent_task']:
                    self.parent_task_id = cleaned_data['parent_task'].id
        
        form_data = FormData(form.cleaned_data)
        return TaskService.create_task(user, form_data)
    
    @staticmethod
    def update_task_from_form(task, form, user):
        """Update task from web form data"""
        # Convert form data to service-compatible format
        class FormData:
            def __init__(self, cleaned_data):
                for key, value in cleaned_data.items():
                    setattr(self, key, value)
                # Handle many-to-many fields
                if 'assigned_to' in cleaned_data:
                    self.assigned_to_ids = [user.id for user in cleaned_data['assigned_to']]
                if 'tags' in cleaned_data:
                    self.tag_ids = [tag.id for tag in cleaned_data['tags']]
                # Handle foreign key fields that need _id suffix
                if 'team' in cleaned_data and cleaned_data['team']:
                    self.team_id = cleaned_data['team'].id
                if 'parent_task' in cleaned_data and cleaned_data['parent_task']:
                    self.parent_task_id = cleaned_data['parent_task'].id
        
        form_data = FormData(form.cleaned_data)
        return TaskService.update_task(task, user, form_data)
    
    @staticmethod
    def get_dashboard_stats(user):
        """Get dashboard statistics for user"""
        base_query = TaskQueryService.build_filtered_query({'user': user})
        
        stats = {
            'total_tasks': base_query.count(),
            'todo_tasks': base_query.filter(status='todo').count(),
            'in_progress_tasks': base_query.filter(status='in_progress').count(),
            'done_tasks': base_query.filter(status__in=['done', 'completed']).count(),
            'high_priority_tasks': base_query.filter(priority__in=['high', 'critical']).count()
        }
        
        return stats