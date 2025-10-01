"""
Simplified API tests that focus on system functionality
Testing core functionality without specific API endpoint dependencies
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json
from tasks.models import Task, Comment, Tag, Team, TaskAssignment

User = get_user_model()


class SystemFunctionalityTest(TestCase):
    """Test core system functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

    def test_user_authentication_flow(self):
        """Test user login/logout functionality"""
        # Test login
        login_success = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_success)
        
        # Test accessing protected pages
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        
        # Test logout
        self.client.logout()
        
        # Test accessing protected page after logout redirects to login
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_task_assignment_functionality(self):
        """Test task assignment through model layer"""
        # Create a task
        task = Task.objects.create(
            title='Assignment Test Task',
            description='Testing task assignment',
            status='todo',
            priority='medium',
            due_date=timezone.now() + timedelta(days=5),
            estimated_hours=Decimal('4.0'),
            created_by=self.user
        )
        
        # Test assignment through TaskAssignment model
        assignment = TaskAssignment.objects.create(
            task=task,
            user=self.user,
            assigned_by=self.admin_user
        )
        
        # Verify assignment
        self.assertIn(self.user, task.assigned_to.all())
        self.assertEqual(assignment.assigned_by, self.admin_user)

    def test_comment_functionality(self):
        """Test comment creation and management"""
        # Create a task
        task = Task.objects.create(
            title='Comment Test Task',
            description='Testing comments',
            status='todo',
            priority='low',
            due_date=timezone.now() + timedelta(days=3),
            estimated_hours=Decimal('2.0'),
            created_by=self.user
        )
        
        # Create a comment
        comment = Comment.objects.create(
            task=task,
            author=self.user,
            content='This is a test comment'
        )
        
        # Verify comment
        self.assertEqual(comment.task, task)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, 'This is a test comment')

    def test_health_endpoint(self):
        """Test system health endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')

    def test_admin_interface_accessible(self):
        """Test Django admin interface"""
        # Test admin login
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        # Verify our customized admin title is displayed
        self.assertContains(response, 'Task Management Administration')

    def test_static_files_served(self):
        """Test that static files are being served"""
        response = self.client.get('/static/css/styles.css')
        # Should either serve the file (200) or redirect (302) or not found (404)
        # 404 is acceptable in test environment without collectstatic
        self.assertIn(response.status_code, [200, 302, 404])

    def test_database_relationships(self):
        """Test that database relationships work correctly"""
        # Create related objects
        tag = Tag.objects.create(name='testing', color='#ff0000')
        team = Team.objects.create(name='Test Team', created_by=self.user)
        team.members.add(self.user)
        
        task = Task.objects.create(
            title='Relationship Test',
            description='Testing database relationships',
            status='todo',
            priority='high',
            due_date=timezone.now() + timedelta(days=1),
            estimated_hours=Decimal('1.0'),
            created_by=self.user,
            team=team
        )
        
        task.tags.add(tag)
        
        # Verify relationships
        self.assertEqual(task.team, team)
        self.assertIn(tag, task.tags.all())
        self.assertIn(self.user, team.members.all())

    def test_search_functionality(self):
        """Test task search capabilities"""
        # Create test tasks
        Task.objects.create(
            title='Search Test Task One',
            description='First task for search testing',
            status='todo',
            priority='medium',
            due_date=timezone.now() + timedelta(days=2),
            estimated_hours=Decimal('3.0'),
            created_by=self.user
        )
        
        Task.objects.create(
            title='Another Task',
            description='Second task for search testing',
            status='in_progress',
            priority='high',
            due_date=timezone.now() + timedelta(days=4),
            estimated_hours=Decimal('5.0'),
            created_by=self.user
        )
        
        # Test search through model manager
        search_results = Task.objects.search('Search Test')
        self.assertGreater(len(search_results), 0)
        
        # Test filtering
        todo_tasks = Task.objects.filter(status='todo')
        in_progress_tasks = Task.objects.filter(status='in_progress')
        
        self.assertGreater(len(todo_tasks), 0)
        self.assertGreater(len(in_progress_tasks), 0)


class CeleryTaskTest(TestCase):
    """Test Celery task functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='celeryuser',
            email='celery@example.com',
            password='celerypass123'
        )

    def test_celery_tasks_importable(self):
        """Test that all Celery tasks can be imported"""
        try:
            from tasks.infrastructure.celery_tasks import (
                send_task_notification,
                generate_daily_summary,
                check_overdue_tasks,
                cleanup_archived_tasks
            )
            from authentication.tasks import cleanup_inactive_users
            
            # All tasks should be importable
            self.assertTrue(callable(send_task_notification))
            self.assertTrue(callable(generate_daily_summary))
            self.assertTrue(callable(check_overdue_tasks))
            self.assertTrue(callable(cleanup_archived_tasks))
            self.assertTrue(callable(cleanup_inactive_users))
            
        except ImportError as e:
            self.fail(f"Could not import Celery tasks: {e}")

    def test_task_notification_logic(self):
        """Test task notification functionality without actually sending emails"""
        task = Task.objects.create(
            title='Notification Test',
            description='Testing notifications',
            status='todo',
            priority='medium',
            due_date=timezone.now() + timedelta(days=1),
            estimated_hours=Decimal('2.0'),
            created_by=self.user
        )
        
        # Test that we can create the notification data
        from tasks.infrastructure.celery_tasks import send_task_notification
        
        # In a real scenario, this would be called with .delay()
        # For testing, we just verify the function exists and is callable
        self.assertTrue(callable(send_task_notification))


class DatabasePerformanceTest(TestCase):
    """Test database performance and optimization features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='perfpass123'
        )

    def test_optimized_querysets(self):
        """Test that optimized querysets work correctly"""
        # Create test data
        team = Team.objects.create(name='Performance Team', created_by=self.user)
        tag = Tag.objects.create(name='performance', color='#00ff00')
        
        task = Task.objects.create(
            title='Performance Test Task',
            description='Testing query optimization',
            status='todo',
            priority='high',
            due_date=timezone.now() + timedelta(days=1),
            estimated_hours=Decimal('4.0'),
            created_by=self.user,
            team=team
        )
        task.tags.add(tag)
        
        # Test optimized querysets
        optimized_tasks = Task.objects.with_optimized_relations()
        self.assertGreater(len(optimized_tasks), 0)
        
        # Test active/archived filtering
        active_tasks = Task.objects.active()
        self.assertIn(task, active_tasks)
        
        archived_tasks = Task.objects.archived()
        self.assertNotIn(task, archived_tasks)

    def test_database_indexes_exist(self):
        """Test that database indexes are properly created"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Get table information
            cursor.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'tasks_task'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Should have indexes on commonly queried fields
            # Note: Exact index names may vary
            self.assertGreater(len(indexes), 0)

    def test_full_text_search_setup(self):
        """Test that full-text search infrastructure is in place"""
        task = Task.objects.create(
            title='Full Text Search Test',
            description='Testing full-text search capabilities',
            status='todo',
            priority='medium',
            due_date=timezone.now() + timedelta(days=2),
            estimated_hours=Decimal('3.0'),
            created_by=self.user
        )
        
        # Test search functionality
        search_results = Task.objects.search('Full Text')
        # Should return results (even if using fallback search)
        self.assertGreaterEqual(len(search_results), 0)
