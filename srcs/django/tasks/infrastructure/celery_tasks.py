"""
Celery tasks for the task management system
"""

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_task_notification(task_id, notification_type):
    """Send email notifications for task events"""
    try:
        from tasks.models import Task
        
        task = Task.objects.get(id=task_id)
        
        if notification_type == 'assigned':
            # Notify assigned users
            assigned_users = task.assigned_to.all()
            for user in assigned_users:
                send_mail(
                    subject=f'Task Assigned: {task.title}',
                    message=f'You have been assigned to task: {task.title}\n\nDescription: {task.description}\n\nDue Date: {task.due_date}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            logger.info(f"Assignment notifications sent for task {task_id}")
            
        elif notification_type == 'due_soon':
            # Notify about upcoming due date
            assigned_users = task.assigned_to.all()
            for user in assigned_users:
                send_mail(
                    subject=f'Task Due Soon: {task.title}',
                    message=f'Task "{task.title}" is due soon: {task.due_date}\n\nDescription: {task.description}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            logger.info(f"Due soon notifications sent for task {task_id}")
            
        elif notification_type == 'overdue':
            # Notify about overdue task
            assigned_users = task.assigned_to.all()
            for user in assigned_users:
                send_mail(
                    subject=f'Task Overdue: {task.title}',
                    message=f'Task "{task.title}" is overdue!\n\nDue Date: {task.due_date}\nDescription: {task.description}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            logger.info(f"Overdue notifications sent for task {task_id}")
            
        return f"Notification sent for task {task_id} - type: {notification_type}"
        
    except Exception as e:
        logger.error(f"Error sending notification for task {task_id}: {e}")
        return f"Error: {e}"


@shared_task
def generate_daily_summary():
    """Generate daily task summary for all users"""
    try:
        from tasks.models import Task
        
        today = timezone.now().date()
        users_with_tasks = User.objects.filter(assigned_tasks__isnull=False).distinct()
        
        for user in users_with_tasks:
            # Get user's tasks
            user_tasks = Task.objects.filter(assigned_to=user, is_archived=False)
            
            # Count tasks by status
            todo_count = user_tasks.filter(status='todo').count()
            in_progress_count = user_tasks.filter(status='in_progress').count()
            review_count = user_tasks.filter(status='review').count()
            done_today = user_tasks.filter(
                status='done',
                updated_at__date=today
            ).count()
            
            # Get overdue tasks
            overdue_tasks = user_tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['todo', 'in_progress', 'review']
            )
            
            # Send daily summary email
            summary_message = f"""
Daily Task Summary for {user.get_full_name() or user.username}

Tasks Overview:
- To Do: {todo_count}
- In Progress: {in_progress_count}
- In Review: {review_count}
- Completed Today: {done_today}
- Overdue: {overdue_tasks.count()}

"""
            
            if overdue_tasks.exists():
                summary_message += "\nOverdue Tasks:\n"
                for task in overdue_tasks[:5]:  # Limit to 5 tasks
                    summary_message += f"- {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})\n"
            
            send_mail(
                subject=f'Daily Task Summary - {today.strftime("%Y-%m-%d")}',
                message=summary_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            
        logger.info(f"Daily summaries sent to {users_with_tasks.count()} users")
        return f"Daily summary sent to {users_with_tasks.count()} users"
        
    except Exception as e:
        logger.error(f"Error generating daily summary: {e}")
        return f"Error: {e}"


@shared_task
def check_overdue_tasks():
    """Mark tasks that are overdue and notify assignees"""
    try:
        from tasks.models import Task, TaskHistory
        
        now = timezone.now()
        
        # Find tasks that are overdue but not marked as such
        overdue_tasks = Task.objects.filter(
            due_date__lt=now,
            status__in=['todo', 'in_progress', 'review'],
            is_overdue=False,
            is_archived=False
        )
        
        updated_count = 0
        
        for task in overdue_tasks:
            # Mark as overdue
            task.is_overdue = True
            task.save()
            
            # Log the change
            TaskHistory.objects.create(
                task=task,
                user=task.created_by,  # System user
                action='updated',
                changes={'is_overdue': True, 'reason': 'automatically_marked_overdue'}
            )
            
            # Send notification
            send_task_notification.delay(task.id, 'overdue')
            
            updated_count += 1
        
        logger.info(f"Marked {updated_count} tasks as overdue")
        return f"Marked {updated_count} tasks as overdue"
        
    except Exception as e:
        logger.error(f"Error checking overdue tasks: {e}")
        return f"Error: {e}"


@shared_task
def cleanup_archived_tasks():
    """Delete archived tasks older than 30 days to no overload the database"""
    try:
        from tasks.models import Task
        
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        
        # Find archived tasks older than 30 days
        old_archived_tasks = Task.objects.filter(
            is_archived=True,
            updated_at__lt=cutoff_date
        )
        
        deleted_count = old_archived_tasks.count()
        old_archived_tasks.delete()
        
        logger.info(f"Deleted {deleted_count} old archived tasks")
        return f"Deleted {deleted_count} old archived tasks"
        
    except Exception as e:
        logger.error(f"Error cleaning up archived tasks: {e}")
        return f"Error: {e}"


########################################################################################

# TODO: Future feature - Auto-assignment of tasks
# Currently not in use but ready to be activated when needed
# To enable: Add to CELERY_BEAT_SCHEDULE in settings.py
"""
@shared_task
def auto_assign_tasks():
    \"\"\"Auto-assign tasks based on workload and availability\"\"\"
    try:
        from tasks.models import Task, TaskAssignment
        
        # Find unassigned tasks
        unassigned_tasks = Task.objects.filter(
            assigned_to__isnull=True,
            status='todo',
            is_archived=False
        )
        
        assigned_count = 0
        
        for task in unassigned_tasks:
            # Simple algorithm: assign to user with least active tasks
            
            if task.team:
                # Assign within team
                team_members = task.team.members.all()
                if team_members.exists():
                    # Find team member with least active tasks
                    least_busy_user = min(
                        team_members,
                        key=lambda u: u.assigned_tasks.filter(
                            status__in=['todo', 'in_progress'],
                            is_archived=False
                        ).count()
                    )
                    
                    # Create assignment
                    TaskAssignment.objects.create(
                        task=task,
                        user=least_busy_user,
                        assigned_by=task.created_by,
                        is_primary=True
                    )
                    
                    # Send notification
                    send_task_notification.delay(task.id, 'assigned')
                    
                    assigned_count += 1
        
        logger.info(f"Auto-assigned {assigned_count} tasks")
        return f"Auto-assigned {assigned_count} tasks"
        
    except Exception as e:
        logger.error(f"Error auto-assigning tasks: {e}")
        return f"Error: {e}"
"""


# TODO: Future feature - Team velocity metrics
# Currently not in use but ready to be activated when needed  
# To enable: Add to CELERY_BEAT_SCHEDULE in settings.py
"""
@shared_task  
def calculate_team_velocity():
    \"\"\"Calculate team velocity metrics\"\"\"
    try:
        from tasks.models import Task, Team
        
        # Calculate for the last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=30)
        
        teams = Team.objects.all()
        
        for team in teams:
            completed_tasks = Task.objects.filter(
                team=team,
                status='done',
                updated_at__date__range=[start_date, end_date]
            )
            
            total_estimated_hours = sum(
                task.estimated_hours for task in completed_tasks
            )
            
            total_actual_hours = sum(
                task.actual_hours or 0 for task in completed_tasks
            )
            
            velocity_data = {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'completed_tasks': completed_tasks.count(),
                'total_estimated_hours': float(total_estimated_hours),
                'total_actual_hours': float(total_actual_hours),
                'efficiency': (
                    float(total_estimated_hours / total_actual_hours) 
                    if total_actual_hours > 0 else 0
                )
            }

            logger.info(f"Team {team.name} velocity: {velocity_data}")
        
        return f"Calculated velocity for {teams.count()} teams"
        
    except Exception as e:
        logger.error(f"Error calculating team velocity: {e}")
        return f"Error: {e}"
"""
