"""
Task Model Mixins and Configurations

Mixins are auxiliary classes that encapsulate specific behaviors or properties
to be shared across multiple models. This helps keep models.py file clean
and focused on the core model definitions and no duplicated code.

"""

from django.db import models
from django.contrib.postgres.indexes import GinIndex


class TaskPropertiesMixin:
    """Mixin providing computed properties for Task model"""
    
    @property
    def is_past_due(self):
        """Check if task is past due date"""
        from .core.business import TaskCalculationUtils
        return TaskCalculationUtils.is_task_overdue(self)
    
    @property
    def progress_percentage(self):
        """Calculate progress based on subtasks"""
        from .core.business import TaskCalculationUtils
        return TaskCalculationUtils.calculate_progress_percentage(self)
    
    @property
    def hours_worked(self):
        """Get actual hours worked on this task (from Task.actual_hours field)"""
        return self.actual_hours or 0
    
    @property
    def hours_remaining(self):
        """Get remaining estimated hours based on actual hours worked"""
        if not self.estimated_hours:
            return 0
        return max(0, float(self.estimated_hours) - float(self.hours_worked))
    
    @property
    def is_over_budget(self):
        """Check if task has exceeded estimated hours budget"""
        if not self.estimated_hours:
            return False
        return self.hours_worked > float(self.estimated_hours)


class TaskValidationMixin:
    """Mixin providing validation functionality for Task model"""
    
    def clean(self):
        """Custom validation using task helpers"""
        from .core.business import TaskValidationUtils
        TaskValidationUtils.validate_task_hierarchy(self)
        TaskValidationUtils.validate_due_date(self)
        TaskValidationUtils.validate_hours(self)
    
    def save(self, *args, **kwargs):
        """Save with metadata validation only"""
        from .core.business import TaskMetadataUtils
        
        # Ensure metadata has default structure
        TaskMetadataUtils.ensure_default_metadata(self)
        
        # Run validation
        self.full_clean()
        
        # Save the model
        super().save(*args, **kwargs)


class TaskDatabaseConfig:
    """Database configuration for Task model"""
    
    @staticmethod
    def get_meta_class():
        """Returns the Meta class configuration for Task model"""
        
        class Meta:
            ordering = ['-created_at']
            indexes = [
                # Single field indexes
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
                # Business logic constraints at DB level
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
        
        return Meta


class CommentBehaviorMixin:
    """Mixin for Comment model behavior"""
    
    def save(self, *args, **kwargs):
        if self.pk:  # If updating existing comment
            self.is_edited = True
        super().save(*args, **kwargs)


class TimestampMixin(models.Model):
    """Abstract mixin for models that need created/updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class ArchivableMixin(models.Model):
    """Abstract mixin for models that can be archived (soft delete)"""
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        abstract = True