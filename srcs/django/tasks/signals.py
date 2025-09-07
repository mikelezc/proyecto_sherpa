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
    else:
        # Check if status changed
        try:
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
        except Task.DoesNotExist:
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
