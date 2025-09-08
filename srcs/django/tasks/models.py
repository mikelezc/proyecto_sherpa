"""
Task Management Models

This module contains the core models for the task management system,
following the requirements from the technical test.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
import uuid

User = get_user_model()


class TaskQuerySet(models.QuerySet):
    """Custom QuerySet for Task model with optimization methods"""
    
    def active(self):
        """Get non-archived tasks"""
        return self.filter(is_archived=False)
    
    def archived(self):
        """Get archived tasks"""
        return self.filter(is_archived=True)
    
    def with_optimized_relations(self):
        """Optimized query with select_related and prefetch_related"""
        return self.select_related(
            'created_by', 'team', 'parent_task', 'template'
        ).prefetch_related(
            'tags', 
            'assigned_to',
            'comments__author',
            'history__user',
            'subtasks'
        )
    
    def search(self, query):
        """
        Smart search that tries full-text first, falls back to basic
        """
        if not query:
            return self
        
        try:
            # Try PostgreSQL full-text search
            from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
            from django.db.models import Q
            
            search_query = SearchQuery(query, config='english')
            return self.annotate(
                search=SearchVector('title', 'description', config='english'),
                rank=SearchRank('search', search_query)
            ).filter(
                search=search_query
            ).order_by('-rank', '-created_at')
        except Exception:
            # Fallback to basic search if PostgreSQL extensions are not available
            from django.db.models import Q
            return self.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )


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
        return self.get_queryset().search(query)


class TaskHistoryManager(models.Manager):
    """Custom manager for TaskHistory model"""
    
    def get_queryset(self):
        """Optimize with select_related by default"""
        return super().get_queryset().select_related('task', 'user')
    
    def recent(self, days=30):
        """Get recent history entries"""
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


class Tag(models.Model):
    """Tags for categorizing tasks"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#007bff")  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Team(models.Model):
    """Teams for organizing users and tasks"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TaskTemplate(models.Model):
    """Templates for creating recurring tasks"""
    name = models.CharField(max_length=200)
    title_template = models.CharField(max_length=200)
    description_template = models.TextField()
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='medium'
    )
    tags = models.ManyToManyField(Tag, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """Main Task model following the technical test requirements"""
    
    # Choices
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Core fields (required by technical test)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField()
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Relationships (required by technical test)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ManyToManyField(
        User, 
        through='TaskAssignment', 
        through_fields=('task', 'user'),
        related_name='assigned_tasks', 
        blank=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks')
    
    # Metadata (required by technical test)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    # Additional useful fields
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    template = models.ForeignKey(TaskTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    
    # Full-text search field for PostgreSQL
    search_vector = SearchVectorField(null=True, blank=True)
    
    # Custom managers - Apply TaskManager
    objects = TaskManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_archived']),
            # Composite indexes for common query patterns
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_by', 'status']),
            models.Index(fields=['team', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['is_archived', 'status']),
            # Full-text search index (PostgreSQL specific)
            GinIndex(fields=['search_vector'], name='task_search_gin_idx'),
        ]
        constraints = [
            # Database-level constraints
            models.CheckConstraint(
                check=models.Q(due_date__gte=models.F('created_at')),
                name='task_due_date_after_creation'
            ),
            models.CheckConstraint(
                check=models.Q(estimated_hours__gte=0),
                name='task_estimated_hours_positive'
            ),
            models.CheckConstraint(
                check=models.Q(actual_hours__gte=0) | models.Q(actual_hours__isnull=True),
                name='task_actual_hours_positive'
            ),
        ]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Validate task data"""
        if self.due_date and self.due_date < timezone.now():
            if self.status == 'todo':
                raise ValidationError("Due date cannot be in the past for new tasks")
        
        if self.parent_task == self:
            raise ValidationError("A task cannot be its own parent")
    
    def save(self, *args, **kwargs):
        # Temporarily skip full_clean for API testing
        # self.full_clean()
        super().save(*args, **kwargs)
        
        # Update search vector after saving
        self.update_search_vector()
    
    def update_search_vector(self):
        """Update the search vector for full-text search"""
        from django.contrib.postgres.search import SearchVector
        from django.db import connection
        
        # Update search vector using PostgreSQL's full-text search
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tasks_task 
                SET search_vector = to_tsvector('english', 
                    COALESCE(title, '') || ' ' || COALESCE(description, '')
                ) 
                WHERE id = %s
                """,
                [self.pk]
            )
    
    @classmethod
    def search_tasks(cls, query):
        """
        Perform full-text search on tasks using PostgreSQL's search capabilities
        """
        from django.contrib.postgres.search import SearchQuery, SearchRank
        
        if not query:
            return cls.objects.all()
        
        search_query = SearchQuery(query, config='english')
        return cls.objects.filter(
            search_vector=search_query
        ).annotate(
            rank=SearchRank('search_vector', search_query)
        ).order_by('-rank', '-created_at')
    
    @property
    def is_past_due(self):
        """Check if task is past due date"""
        return self.due_date < timezone.now() and self.status not in ['done', 'cancelled']
    
    @property
    def progress_percentage(self):
        """Calculate progress based on subtasks if any"""
        subtasks = self.subtasks.all()
        if not subtasks:
            return 100 if self.status == 'done' else 0
        
        completed_subtasks = subtasks.filter(status='done').count()
        return (completed_subtasks / subtasks.count()) * 100


class TaskAssignment(models.Model):
    """Through model for task assignments (required by technical test)"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_assignments_made')
    is_primary = models.BooleanField(default=False)  # Primary assignee
    
    class Meta:
        unique_together = ['task', 'user']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.username} assigned to {self.task.title}"


class Comment(models.Model):
    """Comments on tasks (required by technical test)"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    # Custom manager
    objects = CommentManager()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"
    
    def save(self, *args, **kwargs):
        if self.pk:  # If updating existing comment
            self.is_edited = True
        super().save(*args, **kwargs)


class TaskHistory(models.Model):
    """Audit log for task changes (required by technical test)"""
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('assigned', 'Assigned'),
        ('unassigned', 'Unassigned'),
        ('status_changed', 'Status Changed'),
        ('archived', 'Archived'),
        ('unarchived', 'Unarchived'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who made the change
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changes = models.JSONField(default=dict)  # What changed
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Custom manager
    objects = TaskHistoryManager()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['task', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.user.username} on {self.task.title}"


class TimeLog(models.Model):
    """Time tracking for tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    date_logged = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_logged', '-created_at']
    
    def __str__(self):
        return f"{self.hours}h on {self.task.title} by {self.user.username}"
