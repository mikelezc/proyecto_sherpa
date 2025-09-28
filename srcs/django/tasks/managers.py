"""
DJANGO MANAGERS - Data Access Layer

ARCHITECTURE:
Frontend/API → Views/Controllers → Models → Managers → QuerySets → Database

Managers are the interface between Django models and the database.
--> They are the entry point for ALL database queries.

DATA FLOW:
1. Controller: Task.objects.for_dashboard(user) 
2. Manager: Executes business logic and optimizations
3. QuerySet: Builds optimized SQL query
4. Database: Executes the query
5. Results: Returns optimized Task objects

"""

from django.db import models
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


class TaskQuerySet(models.QuerySet):
    """
    Custom QuerySet for Task model
    Defines chainable query methods for readable and efficient filtering
    """
    
    def active(self):
        """Filter active tasks (not archived)"""
        return self.filter(is_archived=False)
    
    def archived(self):
        """Filter archived tasks (soft delete)"""
        return self.filter(is_archived=True)

    def by_status(self, status):
        """Filter by specific status (todo, in_progress, done, etc.)"""
        return self.filter(status=status)

    def by_priority(self, priority):
        """Filter by priority (low, medium, high, critical)"""
        return self.filter(priority=priority)

    def overdue(self):
        """Filter overdue tasks"""
        return self.filter(is_overdue=True)

    def for_user(self, user):
        """Tasks assigned to a specific user"""
        return self.filter(assigned_to=user)

    def created_by_user(self, user):
        """Tasks created by a specific user"""
        return self.filter(created_by=user)

    def in_team(self, team):
        """Tasks for a specific team"""
        return self.filter(team=team)
    
    def with_optimized_relations(self):
        """
        Query optimization - Avoids N+1 problem
        
        - select_related: JOINs on FKs (created_by, team, parent_task)
        - prefetch_related: Separate query for M2M (tags, assigned_to, etc.)
        
        Without optimization: 100 tasks = 1 + (100×5) = 501 SQL queries
        With optimization: 100 tasks = 6 SQL queries
        """
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
        """Basic text search (fallback)"""
        if not query:
            return self

        return self.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )

    def search_fulltext(self, query):
        """Advanced search with PostgreSQL full-text search"""
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
    """
    Main Task Manager
    Entry point for ALL Task queries
    """
    
    def get_queryset(self):
        """Custom base QuerySet - returns TaskQuerySet instead of default"""
        return TaskQuerySet(self.model, using=self._db)

    def active(self):
        """Direct access to active tasks from manager"""
        return self.get_queryset().active()

    def archived(self):
        """Direct access to archived tasks from manager"""
        return self.get_queryset().archived()

    def with_optimized_relations(self):
        """Optimized queries from manager"""
        return self.get_queryset().with_optimized_relations()

    def search(self, query):
        """Unified search interface"""
        return self.get_queryset().search_fulltext(query)

    def by_status(self, status):
        """Filter by status from manager"""
        return self.get_queryset().by_status(status)

    def by_priority(self, priority):
        """Filter by priority from manager"""
        return self.get_queryset().by_priority(priority)

    def overdue(self):
        """Overdue tasks from manager"""
        return self.get_queryset().overdue()

    def for_user(self, user):
        """User tasks from manager"""
        return self.get_queryset().for_user(user)

    def created_by_user(self, user):
        """Tasks created by user from manager"""
        return self.get_queryset().created_by_user(user)

    def in_team(self, team):
        """Team tasks from manager"""
        return self.get_queryset().in_team(team)
    
    def for_dashboard(self, user=None):
        """
        DASHBOARD TASKS VIEW - Optimized and Relevant
        1. Only active (non-archived) tasks
        2. Prefetch related data to avoid N+1 queries
		3. If user provided, filter tasks relevant to that user:
           - Tasks created by the user
		   - Tasks assigned to the user
		   - Tasks in teams the user belongs to
		4. Ordered by most recent creation date
        5. Returns a QuerySet ready for display in dashboards
        PURPOSE: Efficiently load tasks for dashboard views with minimal queries
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
        Creates a task and automatically logs its creation in TaskHistory.
        1. Creates the task normally
        2. Automatically creates an entry in TaskHistory
		3. Logs who created the task and the initial status
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
    """
    History Manager
    Manages task changes and audit trails
    """
    
    def by_task(self, task):
        """All history entries for a specific task"""
        return self.get_queryset().filter(task=task)

    def recent_changes(self, days=7):
        """Recent changes within specified days"""
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(timestamp__gte=since)

    def by_user(self, user):
        """Changes made by specific user"""
        return self.get_queryset().filter(user=user)


class CommentManager(models.Manager):
    """
    Comment Manager
    Handles task comments and discussions
    """
    
    def by_task(self, task):
        """All comments for a specific task"""
        return self.get_queryset().filter(task=task).order_by('created_at')

    def recent_activity(self, days=7):
        """Recent comments within specified days"""
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(created_at__gte=since)

    def by_author(self, user):
        """Comments written by specific user"""
        return self.get_queryset().filter(author=user)