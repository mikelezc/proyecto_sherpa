"""
Management command to set up descriptions for periodic tasks

This command automatically configures human-readable descriptions 
for all periodic tasks, making Django Admin more informative and 
professional for system administrators.

Usage:
- Basic setup: python manage.py setup_periodic_task_descriptions
- Force update: python manage.py setup_periodic_task_descriptions --force

Automatically called during project setup.
"""

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask


class Command(BaseCommand):
    help = 'Set up descriptions for periodic tasks in Django Admin'

    # Descriptions for each periodic task
    TASK_DESCRIPTIONS = {
        'cleanup-inactive-users': {
            'description': 'Clean up inactive user accounts that haven\'t been verified or used for extended periods. Helps maintain database hygiene by removing stale user data.',
            'enabled': True
        },
        'check-overdue-tasks': {
            'description': 'Monitor and mark tasks that have passed their due date. Automatically updates task status and sends overdue notifications to assigned users.',
            'enabled': True
        },
        'generate-daily-summary': {
            'description': 'Generate and send daily task summary emails to all users with assigned tasks. Includes task counts by status, completed tasks, and overdue items.',
            'enabled': True
        },
        'cleanup-archived-tasks': {
            'description': 'Remove archived tasks older than 30 days to prevent database bloat. Permanently deletes old completed/cancelled tasks to maintain system performance.',
            'enabled': True
        },
        'weekly-search-maintenance': {
            'description': 'Keeps the search index up to date by reflecting new, updated, or removed tasks, ensuring faster and smoother task searches.',
            'enabled': True
        },
        'celery.backend_cleanup': {
            'description': 'Built-in Celery task to clean up expired task results from the database backend. System maintenance task that runs automatically.',
            'enabled': True
        }
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update descriptions even if already set',
        )

    def handle(self, *args, **options):
        force_update = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Setting up periodic task descriptions...')
        )
        
        updated_count = 0
        skipped_count = 0
        
        try:
            for task_name, task_info in self.TASK_DESCRIPTIONS.items():
                try:
                    task = PeriodicTask.objects.get(name=task_name)
                    
                    # Check if description already exists
                    if task.description and not force_update:
                        self.stdout.write(f'⏩ Skipped: {task_name} (already has description)')
                        skipped_count += 1
                        continue
                    
                    # Update description
                    task.description = task_info['description']
                    task.enabled = task_info.get('enabled', True)
                    task.save()
                    
                    self.stdout.write(f'✅ Updated: {task_name}')
                    updated_count += 1
                    
                except PeriodicTask.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Task not found: {task_name}')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error updating descriptions: {e}')
            )
            return
            
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'✅ Setup completed!')
        )
        self.stdout.write(f'   📝 Updated: {updated_count} tasks')
        self.stdout.write(f'   ⏩ Skipped: {skipped_count} tasks')
        self.stdout.write('')
        self.stdout.write('💡 You can now see detailed descriptions in Django Admin > Periodic Tasks')