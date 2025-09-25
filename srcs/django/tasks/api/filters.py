"""
Task API Filters

Query filtering and search functionality for tasks.
Centralizes all filtering logic and provides reusable query builders.
"""

from typing import Optional
from django.db.models import QuerySet, Q
from tasks.models import Task


class TaskFilter:
    """Filter builder for task queries"""
    
    def __init__(self, queryset: Optional[QuerySet] = None):
        self.queryset = queryset or self._get_base_queryset()
    
    @staticmethod
    def _get_base_queryset() -> QuerySet:
        """Get the base queryset for tasks with optimized relations"""
        return Task.objects.filter(
            is_archived=False
        ).select_related(
            'created_by', 'team'
        ).prefetch_related(
            'assigned_to', 'tags'
        )
    
    def by_status(self, status: str) -> 'TaskFilter':
        """Filter tasks by status"""
        if status:
            self.queryset = self.queryset.filter(status=status)
        return self
    
    def by_priority(self, priority: str) -> 'TaskFilter':
        """Filter tasks by priority"""
        if priority:
            self.queryset = self.queryset.filter(priority=priority)
        return self
    
    def assigned_to_user(self, user_id: int) -> 'TaskFilter':
        """Filter tasks assigned to specific user"""
        if user_id:
            self.queryset = self.queryset.filter(assigned_to=user_id)
        return self
    
    def assigned_to_me(self, user, assigned_to_me: bool) -> 'TaskFilter':
        """Filter tasks assigned to the requesting user"""
        if assigned_to_me and user:
            self.queryset = self.queryset.filter(assigned_to=user)
        return self
    
    def created_by_user(self, user_id: int) -> 'TaskFilter':
        """Filter tasks created by specific user"""
        if user_id:
            self.queryset = self.queryset.filter(created_by=user_id)
        return self
    
    def by_team(self, team_id: int) -> 'TaskFilter':
        """Filter tasks by team"""
        if team_id:
            self.queryset = self.queryset.filter(team_id=team_id)
        return self
    
    def with_tag(self, tag_name: str) -> 'TaskFilter':
        """Filter tasks with specific tag"""
        if tag_name:
            self.queryset = self.queryset.filter(tags__name__icontains=tag_name)
        return self
    
    def is_overdue(self, overdue: bool) -> 'TaskFilter':
        """Filter overdue tasks"""
        if overdue is not None:
            self.queryset = self.queryset.filter(is_past_due=overdue)
        return self
    
    def search(self, search_term: str) -> 'TaskFilter':
        """Search tasks by title and description"""
        if search_term:
            # Try to use the model's search method if available
            try:
                self.queryset = Task.search_tasks(search_term)
            except AttributeError:
                # Fallback to basic text search
                self.queryset = self.queryset.filter(
                    models.Q(title__icontains=search_term) |
                    models.Q(description__icontains=search_term)
                )
        return self
    
    def order_by_created(self, descending: bool = True) -> 'TaskFilter':
        """Order tasks by creation date"""
        order_field = '-created_at' if descending else 'created_at'
        self.queryset = self.queryset.order_by(order_field)
        return self
    
    def order_by_due_date(self, descending: bool = False) -> 'TaskFilter':
        """Order tasks by due date"""
        order_field = '-due_date' if descending else 'due_date'
        self.queryset = self.queryset.order_by(order_field)
        return self
    
    def order_by_priority(self, descending: bool = True) -> 'TaskFilter':
        """Order tasks by priority (using priority field order)"""
        # Assuming priority has specific ordering (e.g., critical, high, medium, low)
        priority_order = ['critical', 'high', 'medium', 'low']
        if descending:
            priority_order = priority_order[::-1]
        
        # Create CASE WHEN ordering
        from django.db.models import Case, When, Value, IntegerField
        order_cases = [
            When(priority=priority, then=Value(i)) 
            for i, priority in enumerate(priority_order)
        ]
        self.queryset = self.queryset.annotate(
            priority_order=Case(*order_cases, output_field=IntegerField())
        ).order_by('priority_order')
        return self
    
    def get_queryset(self) -> QuerySet:
        """Get the filtered queryset"""
        return self.queryset
    
    @classmethod
    def build_from_params(cls, **params) -> QuerySet:
        """Build a filtered queryset from dictionary parameters"""
        filter_builder = cls()
        
        # Apply filters based on parameters
        if 'status' in params:
            filter_builder = filter_builder.by_status(params['status'])
        
        if 'priority' in params:
            filter_builder = filter_builder.by_priority(params['priority'])
        
        if 'assigned_to' in params:
            filter_builder = filter_builder.assigned_to_user(params['assigned_to'])
        
        if 'assigned_to_me' in params and 'user' in params:
            filter_builder = filter_builder.assigned_to_me(
                params['user'], 
                params['assigned_to_me']
            )
        
        if 'created_by' in params:
            filter_builder = filter_builder.created_by_user(params['created_by'])
        
        if 'team_id' in params:
            filter_builder = filter_builder.by_team(params['team_id'])
        
        if 'tag' in params:
            filter_builder = filter_builder.with_tag(params['tag'])
        
        if 'is_overdue' in params:
            filter_builder = filter_builder.is_overdue(params['is_overdue'])
        
        if 'search' in params:
            filter_builder = filter_builder.search(params['search'])
        
        # Apply ordering
        if 'order_by' in params:
            order_by = params['order_by']
            descending = params.get('desc', False)
            
            if order_by == 'created_at':
                filter_builder = filter_builder.order_by_created(descending)
            elif order_by == 'due_date':
                filter_builder = filter_builder.order_by_due_date(descending)
            elif order_by == 'priority':
                filter_builder = filter_builder.order_by_priority(descending)
        else:
            # Default ordering
            filter_builder = filter_builder.order_by_created(descending=True)
        
        return filter_builder.get_queryset()


class TaskFilterParams:
    """Helper class to parse and validate filter parameters"""
    
    VALID_STATUSES = ['todo', 'in_progress', 'review', 'done', 'cancelled']
    VALID_PRIORITIES = ['low', 'medium', 'high', 'critical']
    VALID_ORDER_BY = ['created_at', 'due_date', 'priority']
    
    @classmethod
    def parse_bool(cls, value) -> Optional[bool]:
        """Parse boolean parameter from string"""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return None
    
    @classmethod
    def validate_status(cls, status: str) -> Optional[str]:
        """Validate status parameter"""
        if status and status in cls.VALID_STATUSES:
            return status
        return None
    
    @classmethod
    def validate_priority(cls, priority: str) -> Optional[str]:
        """Validate priority parameter"""
        if priority and priority in cls.VALID_PRIORITIES:
            return priority
        return None
    
    @classmethod
    def validate_order_by(cls, order_by: str) -> Optional[str]:
        """Validate order_by parameter"""
        if order_by and order_by in cls.VALID_ORDER_BY:
            return order_by
        return None