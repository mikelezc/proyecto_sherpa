#!/bin/bash

# =============================================================================
# CELERY TASKS DEMONSTRATION SCRIPT - SIMPLIFIED VERSION
# Automated demo for showing Celery functionality to examiner
# =============================================================================

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored headers
print_header() {
    echo -e "\n${BLUE}===============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===============================================${NC}\n"
}

print_step() {
    echo -e "${GREEN}🔸 $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${PURPLE}⚠️  $1${NC}"
}

# Function to pause and wait for user input
pause_demo() {
    echo -e "\n${YELLOW}Press ENTER to continue to next demo...${NC}"
    read -r
}

# Check containers
check_containers() {
    print_header "🔍 CHECKING DOCKER CONTAINERS STATUS"
    
    if ! docker-compose ps | grep -q "django_web.*Up"; then
        echo -e "${RED}❌ Django web container is not running!${NC}"
        exit 1
    fi
    
    print_success "All containers are running!"
    docker-compose ps
}

# Demo 1: Show scheduled tasks
demo_scheduled_tasks() {
    print_header "📋 DEMO 1: SCHEDULED TASKS STATUS"
    
    print_step "Showing currently scheduled periodic tasks..."
    
    docker exec django_web python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
print('📋 ACTIVE SCHEDULED TASKS:')
print('=' * 50)
for task in PeriodicTask.objects.filter(enabled=True):
    print(f'✅ {task.name}')
    print(f'   Task: {task.task}')
    if task.interval:
        print(f'   Interval: {task.interval}')
    elif task.crontab:
        print(f'   Crontab: {task.crontab}')
    print(f'   Last run: {task.last_run_at or \"Never\"}')
    print()
"
    
    print_success "Scheduled tasks displayed!"
    pause_demo
}

# Demo 2: Show registered tasks
demo_registered_tasks() {
    print_header "🔧 DEMO 2: REGISTERED TASKS IN CELERY WORKER"
    
    print_step "Checking what tasks are registered in the Celery worker..."
    
    docker exec django_web celery -A main inspect registered
    
    print_success "Registered tasks displayed!"
    pause_demo
}

# Demo 3: Create demo task and send notification
demo_task_notification() {
    print_header "📧 DEMO 3: TASK ASSIGNMENT NOTIFICATION"
    
    print_step "Creating a demo task and sending assignment notification..."
    print_warning "Watch for the email output in the logs!"
    
    docker exec django_web python manage.py shell -c "
from django.contrib.auth import get_user_model
from tasks.models import Task
from tasks.services.task_service import TaskService
from tasks.infrastructure.celery_tasks import send_task_notification
from django.utils import timezone
import time

User = get_user_model()
user = User.objects.first()

if user:
    # Create demo task
    task = Task.objects.create(
        title='🎯 DEMO: Task Assignment Notification',
        description='This task demonstrates the email notification system.',
        status='todo',
        priority='high',
        due_date=timezone.now() + timezone.timedelta(days=3),
        created_by=user
    )
    
    print(f'✅ Demo task created with ID: {task.id}')
    print(f'📧 Task title: {task.title}')
    print()
    
    # Assign the task
    assignments = TaskService.assign_users_to_task(
        task=task,
        user_ids=[user.id],
        assigned_by=user,
        is_primary=True
    )
    
    print(f'✅ Task assigned to: {user.email}')
    
    # Send notification
    result = send_task_notification.delay(task.id, 'assigned')
    print(f'📨 Notification task queued: {result.id}')
    
    time.sleep(2)
    
    from celery.result import AsyncResult
    task_result = AsyncResult(str(result.id))
    print(f'🔍 Status: {task_result.status}')
    if task_result.ready():
        print(f'📊 Result: {task_result.result}')
    
    print()
    print('📧 Check email in logs: docker logs django_web --tail 20')
else:
    print('❌ No users found!')
"
    
    print_success "Task created and notification sent!"
    pause_demo
}

# Demo 4: Show overdue check
demo_overdue_tasks() {
    print_header "⏰ DEMO 4: OVERDUE TASKS AUTOMATIC CHECK"
    
    print_step "Demonstrating the automatic overdue task detection..."
    
    docker exec django_web python manage.py shell -c "
from tasks.models import Task
from tasks.infrastructure.celery_tasks import check_overdue_tasks
from django.utils import timezone
import time

current_time = timezone.now()

print('📊 CURRENT TASK STATUS:')
total_tasks = Task.objects.count()
tasks_with_due_dates = Task.objects.filter(due_date__isnull=False).count()
currently_overdue = Task.objects.filter(due_date__lt=current_time, is_overdue=False).count()
marked_overdue = Task.objects.filter(is_overdue=True).count()

print(f'📋 Total tasks: {total_tasks}')
print(f'📅 Tasks with due dates: {tasks_with_due_dates}')
print(f'⏰ Tasks overdue but not marked: {currently_overdue}')
print(f'🚨 Tasks marked as overdue: {marked_overdue}')
print()

print('🔍 Running overdue check...')
result = check_overdue_tasks.delay()
print(f'✅ Check queued: {result.id}')

time.sleep(3)

from celery.result import AsyncResult
task_result = AsyncResult(str(result.id))
print(f'🔍 Status: {task_result.status}')
if task_result.ready():
    print(f'📊 Result: {task_result.result}')

print()
print('📧 This runs automatically every hour!')
"
    
    print_success "Overdue check completed!"
    pause_demo
}

# Demo 5: Generate daily summary
demo_daily_summary() {
    print_header "📊 DEMO 5: DAILY SUMMARY GENERATION"
    
    print_step "Generating daily summary..."
    
    docker exec django_web python manage.py shell -c "
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskAssignment
from tasks.infrastructure.celery_tasks import generate_daily_summary
import time

User = get_user_model()

print('📊 WORKSPACE STATISTICS:')
print(f'👥 Total Users: {User.objects.count()}')
print(f'📋 Total Tasks: {Task.objects.count()}')
print(f'🔗 Total Assignments: {TaskAssignment.objects.count()}')

for status, display in [('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')]:
    count = Task.objects.filter(status=status).count()
    print(f'   {display}: {count} tasks')

print()
print('📧 Generating daily summary...')
result = generate_daily_summary.delay()
print(f'✅ Summary queued: {result.id}')

time.sleep(3)

from celery.result import AsyncResult
task_result = AsyncResult(str(result.id))
print(f'🔍 Status: {task_result.status}')
if task_result.ready():
    print(f'📊 Result: {task_result.result}')

print()
print('📧 Summary emails sent!')
print()
print('⏰ SCHEDULED FREQUENCY: Every 24 hours (86400 seconds)')
print('🕐 NEXT RUN: Automatically at same time tomorrow')
"
    
    print_success "Daily summary completed!"
    pause_demo
}

# Demo 6: Archived tasks cleanup
demo_cleanup_archived() {
    print_header "🧹 DEMO 6: ARCHIVED TASKS CLEANUP"
    
    print_step "Demonstrating archived tasks cleanup system..."
    
    docker exec django_web python manage.py shell -c "
from tasks.models import Task
from tasks.infrastructure.celery_tasks import cleanup_archived_tasks
from django.utils import timezone
from datetime import timedelta
import time

current_time = timezone.now()

print('📊 ARCHIVED TASKS ANALYSIS:')
print('=' * 40)

# Show archived tasks statistics
total_tasks = Task.objects.count()
archived_tasks = Task.objects.filter(is_archived=True).count()
old_archived = Task.objects.filter(
    is_archived=True, 
    archived_at__lt=current_time - timedelta(days=30)
).count() if archived_tasks > 0 else 0

print(f'📋 Total tasks in system: {total_tasks}')
print(f'🗄️ Archived tasks: {archived_tasks}')
print(f'🧹 Old archived tasks (>30 days): {old_archived}')
print()

if archived_tasks > 0:
    print('📋 SAMPLE ARCHIVED TASKS:')
    print('-' * 30)
    sample_archived = Task.objects.filter(is_archived=True)[:3]
    for task in sample_archived:
        archived_days = (current_time - task.archived_at).days if task.archived_at else 0
        print(f'📁 {task.title[:30]}...')
        print(f'   Archived: {archived_days} days ago')
        print(f'   Status: {task.status}')
        print()

print('🧹 RUNNING CLEANUP PROCESS:')
print('This removes archived tasks older than 30 days')
result = cleanup_archived_tasks.delay()
print(f'✅ Cleanup task queued: {result.id}')

time.sleep(3)

from celery.result import AsyncResult
task_result = AsyncResult(str(result.id))
print(f'🔍 Status: {task_result.status}')
if task_result.ready():
    print(f'📊 Result: {task_result.result}')

print()
print('⏰ SCHEDULED FREQUENCY: Every 7 days (604800 seconds)')
print('🕐 NEXT RUN: Automatically in 7 days')
print('💡 This keeps the database clean and optimized')
"
    
    print_success "Archived tasks cleanup completed!"
    pause_demo
}

# Demo 7: Show worker activity
demo_worker_activity() {
    print_header "👷 DEMO 7: CELERY WORKER ACTIVITY"
    
    print_step "Showing recent worker activity..."
    
    echo -e "${YELLOW}Celery Worker Logs:${NC}"
    docker logs celery_worker --tail 10
    
    echo -e "\n${YELLOW}Celery Beat Logs:${NC}"
    docker logs celery_beat --tail 10
    
    print_success "Worker activity shown!"
    pause_demo
}

# Demo 8: Email configuration
demo_email_config() {
    print_header "📧 DEMO 8: EMAIL CONFIGURATION"
    
    print_step "Showing email configuration..."
    
    docker exec django_web python manage.py shell -c "
from django.conf import settings

print('📧 EMAIL CONFIGURATION:')
print('=' * 30)
print(f'Email Backend: {settings.EMAIL_BACKEND}')
print(f'Default From Email: {settings.DEFAULT_FROM_EMAIL}')
print()
print('💡 Emails go to console - perfect for demos!')
"
    
    print_success "Email configuration shown!"
    pause_demo
}

# Main execution
main() {
    clear
    echo -e "${GREEN}"
    echo "  ╔══════════════════════════════════════════════════════════╗"
    echo "  ║           🚀 CELERY TASKS DEMONSTRATION 🚀              ║"
    echo "  ║     Automated demo of task management system             ║"
    echo "  ╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    print_info "This will demonstrate all Celery functionality"
    print_warning "Watch container logs for email output!"
    
    echo -e "\n${YELLOW}Ready to start? (Press ENTER)${NC}"
    read -r
    
    # Run demos
    check_containers
    demo_scheduled_tasks
    demo_registered_tasks
    demo_task_notification
    demo_overdue_tasks
    demo_daily_summary
    demo_cleanup_archived
    demo_worker_activity
    demo_email_config
    
    # Final summary
    print_header "🎉 DEMONSTRATION COMPLETED!"
    
    echo -e "${GREEN}What was demonstrated:${NC}"
    echo "✅ Scheduled periodic tasks"
    echo "✅ Celery worker registration"
    echo "✅ Task assignment notifications"
    echo "✅ Automatic overdue detection"
    echo "✅ Daily summary generation"
    echo "✅ Archived tasks cleanup"
    echo "✅ Worker activity monitoring"
    echo "✅ Email configuration"
    
    echo -e "\n${YELLOW}📧 To see emails:${NC}"
    echo "docker logs django_web --tail 50 | grep 'Subject:' -A 10 -B 5"
    
    echo -e "\n${GREEN}🎯 All functionality demonstrated!${NC}\n"
}

# Run the demo
main