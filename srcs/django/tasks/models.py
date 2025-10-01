"""
Task Management Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVectorField
from .managers import TaskManager, TaskHistoryManager, CommentManager
from .mixins import *
from .constants import *

User = get_user_model()


class Tag(models.Model):
    """Tags for categorizing tasks"""
    name = models.CharField(max_length=MAX_TAG_NAME_LENGTH, unique=True)
    color = models.CharField(max_length=MAX_COLOR_LENGTH, default=DEFAULT_TAG_COLOR)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Team(models.Model):
    """Teams for organizing users and tasks"""
    name = models.CharField(max_length=MAX_TEAM_NAME_LENGTH, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Task(TaskPropertiesMixin, TaskValidationMixin, TimestampMixin, ArchivableMixin):
    """Main Task model - Clean field definitions only"""
    
    # Compatibility attributes for backward compatibility (class-level attributes)
    STATUS_CHOICES = TASK_STATUS_CHOICES
    PRIORITY_CHOICES = TASK_PRIORITY_CHOICES
    
    # Core fields
    title = models.CharField(max_length=MAX_TASK_TITLE_LENGTH)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=MAX_STATUS_LENGTH, choices=TASK_STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=MAX_PRIORITY_LENGTH, choices=TASK_PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField()
    estimated_hours = models.DecimalField(max_digits=HOURS_MAX_DIGITS, decimal_places=HOURS_DECIMAL_PLACES, default=0)
    actual_hours = models.DecimalField(max_digits=HOURS_MAX_DIGITS, decimal_places=HOURS_DECIMAL_PLACES, null=True, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ManyToManyField(
        User, 
        through='TaskAssignment', 
        through_fields=('task', 'user'),
        related_name='assigned_tasks', 
        blank=True
    )
    tags = models.ManyToManyField('Tag', blank=True)
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks')
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    # Metadata and search
    metadata = models.JSONField(default=dict, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    
    # Custom manager
    objects = TaskManager()
    
    # Use configuration from mixins
    Meta = TaskDatabaseConfig.get_meta_class()
    
    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    """Through model for task assignments"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_assignments_made')
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['task', 'user']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.username} assigned to {self.task.title}"


class Comment(CommentBehaviorMixin, TimestampMixin):
    """Comments on tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    
    objects = CommentManager()
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class TaskHistory(models.Model):
    """Audit log for task changes"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=MAX_ACTION_LENGTH, choices=TASK_HISTORY_ACTION_CHOICES)
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = TaskHistoryManager()
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['task', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.user.username} on {self.task.title}"
