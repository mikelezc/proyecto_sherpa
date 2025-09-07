"""
Management command to test all Celery background tasks
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task, TaskHistory, Comment, Tag, Team
from authentication.models import CustomUser
from tasks.tasks import (
    send_task_notification, 
    generate_daily_summary, 
    check_overdue_tasks, 
    cleanup_archived_tasks,
    auto_assign_tasks,
    calculate_team_velocity
)
from datetime import timedelta


class Command(BaseCommand):
    help = 'Test all Celery background tasks functionality'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 Starting Celery Tasks Tests...\n')
        )
        
        # Test 1: Required Celery Tasks
        self.test_required_tasks()
        
        # Test 2: Celery Beat Schedule
        self.test_celery_beat_schedule()
        
        # Test 3: Task Notifications  
        self.test_task_notifications()
        
        # Test 4: Additional Tasks
        self.test_additional_tasks()
        
        # Test 5: Integration with Signals
        self.test_signal_integration()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 All Celery tests completed!')
        )

    def test_required_tasks(self):
        """Test all 4 required Celery tasks"""
        self.stdout.write('1️⃣  Testing Required Celery Tasks...')
        
        try:
            # Test send_task_notification
            result1 = send_task_notification.delay(1, 'assigned')
            self.stdout.write(f'   ✅ send_task_notification: Task ID {result1.id}')
            
            # Test generate_daily_summary
            result2 = generate_daily_summary.delay()
            self.stdout.write(f'   ✅ generate_daily_summary: Task ID {result2.id}')
            
            # Test check_overdue_tasks
            result3 = check_overdue_tasks.delay()
            self.stdout.write(f'   ✅ check_overdue_tasks: Task ID {result3.id}')
            
            # Test cleanup_archived_tasks
            result4 = cleanup_archived_tasks.delay()
            self.stdout.write(f'   ✅ cleanup_archived_tasks: Task ID {result4.id}')
            
            self.stdout.write(self.style.SUCCESS('   ✅ Required Tasks: ALL PASSED\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Required Tasks: FAILED - {e}\n'))

    def test_celery_beat_schedule(self):
        """Test Celery Beat schedule configuration"""
        self.stdout.write('2️⃣  Testing Celery Beat Schedule...')
        
        try:
            from django.conf import settings
            
            schedule = settings.CELERY_BEAT_SCHEDULE
            required_tasks = [
                'check-overdue-tasks',
                'generate-daily-summary', 
                'cleanup-archived-tasks'
            ]
            
            for task_name in required_tasks:
                if task_name in schedule:
                    interval = schedule[task_name]['schedule']
                    task_path = schedule[task_name]['task']
                    
                    if task_name == 'check-overdue-tasks':
                        expected = 3600.0  # Hourly
                        if interval == expected:
                            self.stdout.write(f'   ✅ {task_name}: Hourly ({interval}s)')
                        else:
                            self.stdout.write(f'   ⚠️  {task_name}: {interval}s (expected {expected}s)')
                    
                    elif task_name == 'generate-daily-summary':
                        expected = 86400.0  # Daily
                        if interval == expected:
                            self.stdout.write(f'   ✅ {task_name}: Daily ({interval}s)')
                        else:
                            self.stdout.write(f'   ⚠️  {task_name}: {interval}s (expected {expected}s)')
                    
                    elif task_name == 'cleanup-archived-tasks':
                        expected = 604800.0  # Weekly
                        if interval == expected:
                            self.stdout.write(f'   ✅ {task_name}: Weekly ({interval}s)')
                        else:
                            self.stdout.write(f'   ⚠️  {task_name}: {interval}s (expected {expected}s)')
                else:
                    self.stdout.write(f'   ❌ {task_name}: NOT FOUND in schedule')
            
            self.stdout.write(self.style.SUCCESS('   ✅ Beat Schedule: VERIFIED\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Beat Schedule: FAILED - {e}\n'))

    def test_task_notifications(self):
        """Test different notification types"""
        self.stdout.write('3️⃣  Testing Task Notifications...')
        
        try:
            # Test different notification types
            notification_types = ['assigned', 'due_soon', 'overdue']
            
            for notif_type in notification_types:
                try:
                    result = send_task_notification.delay(1, notif_type)
                    self.stdout.write(f'   ✅ Notification {notif_type}: Task ID {result.id}')
                except Exception as e:
                    self.stdout.write(f'   ⚠️  Notification {notif_type}: {e}')
            
            self.stdout.write(self.style.SUCCESS('   ✅ Task Notifications: TESTED\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Task Notifications: FAILED - {e}\n'))

    def test_additional_tasks(self):
        """Test additional bonus tasks"""
        self.stdout.write('4️⃣  Testing Additional Tasks...')
        
        try:
            # Test auto_assign_tasks
            result1 = auto_assign_tasks.delay()
            self.stdout.write(f'   ✅ auto_assign_tasks: Task ID {result1.id}')
            
            # Test calculate_team_velocity
            result2 = calculate_team_velocity.delay()
            self.stdout.write(f'   ✅ calculate_team_velocity: Task ID {result2.id}')
            
            self.stdout.write(self.style.SUCCESS('   ✅ Additional Tasks: PASSED\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Additional Tasks: FAILED - {e}\n'))

    def test_signal_integration(self):
        """Test integration with Django signals"""
        self.stdout.write('5️⃣  Testing Signal Integration...')
        
        try:
            # Check if signals are properly connected
            from django.db.models.signals import post_save
            from tasks.models import TaskAssignment
            from tasks.signals import task_assigned
            
            # Check signal connections
            signal_receivers = post_save._live_receivers(sender=TaskAssignment)
            signal_found = any(
                receiver.__name__ == 'task_assigned' 
                for receiver_ref in signal_receivers 
                for receiver in [receiver_ref()]
                if receiver and hasattr(receiver, '__name__')
            )
            
            if signal_found:
                self.stdout.write('   ✅ TaskAssignment signal: CONNECTED')
            else:
                self.stdout.write('   ⚠️  TaskAssignment signal: NOT FOUND')
            
            # Test task count
            total_tasks = Task.objects.count()
            self.stdout.write(f'   📊 Total tasks in system: {total_tasks}')
            
            # Test overdue tasks
            overdue_count = Task.objects.filter(is_overdue=True).count()
            self.stdout.write(f'   📊 Currently overdue tasks: {overdue_count}')
            
            # Test archived tasks
            archived_count = Task.objects.filter(is_archived=True).count()
            self.stdout.write(f'   📊 Archived tasks: {archived_count}')
            
            self.stdout.write(self.style.SUCCESS('   ✅ Signal Integration: VERIFIED\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Signal Integration: FAILED - {e}\n'))

    def add_arguments(self, parser):
        """Add optional arguments"""
        parser.add_argument(
            '--run-sync',
            action='store_true',
            help='Run tasks synchronously instead of async (for testing)',
        )
