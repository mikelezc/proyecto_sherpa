"""
Custom managers for Task models with optimized queries
"""

from django.db import models
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


class TaskQuerySet(models.QuerySet):
    """Custom QuerySet for Task model with optimization methods"""
    
    def active(self):
        """Get non-archived tasks"""
        return self.filter(is_archived=False)
    
    def archived(self):
        """Get archived tasks"""
        return self.filter(is_archived=True)
    
    def by_status(self, status):
        """Filter by status"""
        return self.filter(status=status)
    
    def by_priority(self, priority):
        """Filter by priority"""
        return self.filter(priority=priority)
    
    def overdue(self):
        """Get overdue tasks"""
        return self.filter(is_overdue=True)
    
    def for_user(self, user):
        """Get tasks assigned to a specific user"""
        return self.filter(assigned_to=user)
    
    def created_by_user(self, user):
        """Get tasks created by a specific user"""
        return self.filter(created_by=user)
    
    def in_team(self, team):
        """Get tasks for a specific team"""
        return self.filter(team=team)
    
    def with_optimized_relations(self):
        """Optimized query with select_related and prefetch_related"""
        return self.select_related(
            'created_by', 'team', 'parent_task'
        ).prefetch_related(
            'tags', 
            'assigned_to',
            'comments__author',
            'history__user',
            'subtasks'
        )
    
    def search_text(self, query):
        """
        Basic text search using icontains for compatibility
        """
        if not query:
            return self
        
        return self.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    def search_fulltext(self, query):
        """
        PostgreSQL full-text search using search vectors
        """
        if not query:
            return self
        
        try:
            # Try to use PostgreSQL full-text search
            search_query = SearchQuery(query, config='english')
            return self.annotate(
                search=SearchVector('title', 'description', config='english'),
                rank=SearchRank('search', search_query)
            ).filter(
                search=search_query
            ).order_by('-rank', '-created_at')
        except Exception:
            # Fallback to basic search if PostgreSQL extensions are not available
            return self.search_text(query)


class TaskManager(models.Manager):
    """Custom manager for Task model"""
    
    def get_queryset(self):
        """Use custom QuerySet"""
        return TaskQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get non-archived tasks"""
        return self.get_queryset().active()
    
    def archived(self):
        """Get archived tasks"""
        return self.get_queryset().archived()
    
    def with_optimized_relations(self):
        """Get tasks with optimized relations"""
        return self.get_queryset().with_optimized_relations()
    
    def search(self, query):
        """
        Smart search that tries full-text first, falls back to basic
        """
        return self.get_queryset().search_fulltext(query)
    
    def for_dashboard(self, user=None):
        """
        Optimized query for dashboard with all necessary relations
        """
        queryset = self.active().with_optimized_relations()
        
        if user:
            # Filter tasks relevant to the user
            queryset = queryset.filter(
                Q(created_by=user) |
                Q(assigned_to=user) |
                Q(team__members=user)
            ).distinct()
        
        return queryset.order_by('-created_at')
    
    def create_with_history(self, **kwargs):
        """
        Create task and automatically create history entry
        """
        task = self.create(**kwargs)
        
        # Import here to avoid circular imports
        from .models import TaskHistory
        
        TaskHistory.objects.create(
            task=task,
            user=task.created_by,
            action='created',
            changes={'status': task.status}
        )
        
        return task


class TaskHistoryManager(models.Manager):
    """Custom manager for TaskHistory model"""
    
    def get_queryset(self):
        """Optimize with select_related by default"""
        return super().get_queryset().select_related('task', 'user')
    
    def for_task(self, task):
        """Get history for a specific task"""
        return self.filter(task=task).order_by('-timestamp')
    
    def by_user(self, user):
        """Get history by a specific user"""
        return self.filter(user=user).order_by('-timestamp')
    
    def recent(self, days=30):
        """Get recent history entries"""
        from django.utils import timezone
        from datetime import timedelta
        
        since_date = timezone.now() - timedelta(days=days)
        return self.filter(timestamp__gte=since_date)


class CommentManager(models.Manager):
    """Custom manager for Comment model"""
    
    def get_queryset(self):
        """Optimize with select_related by default"""
        return super().get_queryset().select_related('task', 'author')
    
    def for_task(self, task):
        """Get comments for a specific task"""
        return self.filter(task=task).order_by('created_at')
    
    def by_author(self, author):
        """Get comments by a specific author"""
        return self.filter(author=author).order_by('-created_at')
