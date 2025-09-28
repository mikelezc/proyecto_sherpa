"""
Django signals for task management automation 
and sending notifications with Celery when tasks are created or updated 
(with assigned users via TaskAssignment)

"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Task, TaskHistory, TaskAssignment
from .infrastructure.celery_tasks import send_task_notification
from .core.business import check_and_update_overdue_status


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
        
        # Search vector update is handled by Task.save() method
    else:
        # Check if status changed
        try:
            # Get the old task from database before update
            old_task = Task.objects.get(pk=instance.pk)
            if old_task.status != instance.status:
                TaskHistory.objects.create(
                    task=instance,
                    user=instance.created_by,
                    action='status_changed',
                    changes={
                        'old_status': old_task.status,
                        'new_status': instance.status
                    }
                )
            
            # Update search vector if title or description changed
            if (old_task.title != instance.title or 
                old_task.description != instance.description):
                # Search vector update is handled by Task.save() method
                pass
                
        except Task.DoesNotExist:
            # Search vector update is handled by Task.save() method
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
    check_and_update_overdue_status(instance)
