"""
Django signals for task management automation 
and sending notifications with Celery when tasks are created or updated 
(with assigned users via TaskAssignment)

"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Task, TaskHistory, TaskAssignment
from .infrastructure.celery_tasks import send_task_notification
from .core.calculations import TaskCalculationUtils

# Variable global para almacenar estados anteriores
_task_previous_state = {}


@receiver(pre_save, sender=Task)
def capture_task_previous_state(sender, instance, **kwargs):
    """Capture task state before save"""
    if instance.pk:
        try:
            old_task = Task.objects.get(pk=instance.pk)
            _task_previous_state[instance.pk] = {
                'status': old_task.status,
                'due_date': old_task.due_date,
                'title': old_task.title,
                'description': old_task.description,
            }
        except Task.DoesNotExist:
            pass


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
        # Check for changes using captured previous state
        previous_state = _task_previous_state.get(instance.pk, {})
        
        if previous_state:
            # Check for status changes
            if previous_state.get('status') != instance.status:
                TaskHistory.objects.create(
                    task=instance,
                    user=instance.created_by,
                    action='status_changed',
                    changes={
                        'old_status': previous_state.get('status'),
                        'new_status': instance.status
                    }
                )
                
                # Send notification for important status changes
                important_statuses = ['review', 'completed', 'cancelled', 'in_progress']
                if instance.status in important_statuses:
                    send_task_notification.delay(instance.id, 'status_changed')
            
            # Check for due date changes
            if previous_state.get('due_date') != instance.due_date:
                TaskHistory.objects.create(
                    task=instance,
                    user=instance.created_by,
                    action='due_date_changed',
                    changes={
                        'old_due_date': previous_state.get('due_date').isoformat() if previous_state.get('due_date') else None,
                        'new_due_date': instance.due_date.isoformat() if instance.due_date else None
                    }
                )
                
                # Send notification for due date changes (only if task has assignments)
                if instance.assigned_to.exists():
                    send_task_notification.delay(instance.id, 'due_date_changed')
            
            # Update search vector if title or description changed
            if (previous_state.get('title') != instance.title or 
                previous_state.get('description') != instance.description):
                # Search vector update is handled by Task.save() method
                pass
            
            # Clean up previous state
            del _task_previous_state[instance.pk]


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
    TaskCalculationUtils.check_and_update_overdue_status(instance)
