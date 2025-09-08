"""
Django signals for task management automation
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task, TaskHistory, TaskAssignment
from .tasks import send_task_notification


@receiver(post_save, sender=Task)
def task_created_or_updated(sender, instance, created, **kwargs):
    """Handle task creation and updates"""
    if created:
        # Log task creation
        TaskHistory.objects.create(
            task=instance,
            user=instance.created_by,
            action='created',
            changes={'status': instance.status}
        )
        
        # Update search vector for new task
        update_task_search_vector(instance)
    else:
        # Check if status changed
        try:
            # Get the old task from database before update
            old_task = Task.objects.get(pk=instance.pk)
            if old_task.status != instance.status:
                TaskHistory.objects.create(
                    task=instance,
                    user=instance.created_by,  # In a real app, you'd track who made the change
                    action='status_changed',
                    changes={
                        'old_status': old_task.status,
                        'new_status': instance.status
                    }
                )
            
            # Update search vector if title or description changed
            if (old_task.title != instance.title or 
                old_task.description != instance.description):
                update_task_search_vector(instance)
                
        except Task.DoesNotExist:
            # Task might be new, update search vector anyway
            update_task_search_vector(instance)


def update_task_search_vector(task_instance):
    """
    Update search vector for full-text search
    """
    try:
        # Use raw SQL to update search vector efficiently
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE tasks_task 
                SET search_vector = to_tsvector('english', 
                    COALESCE(title, '') || ' ' || COALESCE(description, '')
                ) 
                WHERE id = %s
            """, [task_instance.pk])
    except Exception as e:
        # If PostgreSQL full-text search is not available, skip silently
        pass


@receiver(post_save, sender=TaskAssignment)
def task_assigned(sender, instance, created, **kwargs):
    """Handle task assignments"""
    if created:
        # Log the assignment
        TaskHistory.objects.create(
            task=instance.task,
            user=instance.assigned_by,
            action='assigned',
            changes={
                'assigned_to': instance.user.username,
                'is_primary': instance.is_primary
            }
        )
        
        # Send notification asynchronously
        send_task_notification.delay(instance.task.id, 'assigned')


@receiver(pre_save, sender=Task)
def check_task_due_date(sender, instance, **kwargs):
    """Check and update overdue status"""
    if instance.due_date and instance.due_date < timezone.now():
        if instance.status not in ['done', 'cancelled']:
            instance.is_overdue = True
    else:
        instance.is_overdue = False
