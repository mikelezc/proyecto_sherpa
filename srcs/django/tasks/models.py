"""
Task Management Models

Architecture Overview:
- 8 main models covering all aspects of task management
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

# Import custom managers
from .managers import TaskManager, TaskHistoryManager, CommentManager

User = get_user_model()


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
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('completed', 'Completed'),
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
    description = models.TextField(blank=True)
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
    metadata = models.JSONField(default=dict, blank=True)
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
        """Custom validation using business logic"""
        from .business import validate_task_due_date, validate_parent_task
        validate_task_due_date(self)
        validate_parent_task(self)
    
    def save(self, *args, **kwargs):
        """Save with minimal business logic"""
        from .business import validate_metadata, update_task_search_vector
        
        # Ensure metadata has default value
        validate_metadata(self)
        
        # Run validation
        self.full_clean()
        
        # Save the model
        super().save(*args, **kwargs)
        
        # Update search vector after saving
        update_task_search_vector(self.pk)
    
    @classmethod
    def search_tasks(cls, query):
        """Perform full-text search on tasks"""
        from .search import search_tasks
        return search_tasks(cls, query)
    
    @property
    def is_past_due(self):
        """Check if task is past due date"""
        from .business import is_task_overdue
        return is_task_overdue(self)
    
    @property
    def progress_percentage(self):
        """Calculate progress based on subtasks"""
        from .business import calculate_task_progress
        return calculate_task_progress(self)


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
