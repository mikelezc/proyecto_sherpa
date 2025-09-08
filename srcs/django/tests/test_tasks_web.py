"""
Tests for task web interface (templates and views)
"""
import logging
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from tasks.models import Task, Team, Tag, TaskAssignment

User = get_user_model()

# Suppress logging during tests
logging.disable(logging.WARNING)


class TaskWebInterfaceTest(TestCase):
    """Test task web interface functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test team
        self.team = Team.objects.create(
            name='Test Team',
            description='Test team description',
            created_by=self.user
        )
        
        # Create test tag
        self.tag = Tag.objects.create(
            name='Test Tag',
            color='#007bff'
        )
        
        # Add user to team
        self.team.members.add(self.user)
        
        # Set up client and login
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
    def test_task_dashboard_access(self):
        """Test task dashboard is accessible"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task Management')
        
    def test_task_list_access(self):
        """Test task list is accessible"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tasks/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All Tasks')
        
    def test_task_create_page(self):
        """Test task creation page loads correctly"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tasks/tasks/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Task')
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Description')
        self.assertContains(response, 'Assign to Users')
        
    def test_task_create_form_submission(self):
        """Test task creation via form submission"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/tasks/tasks/create/', {
            'title': 'Test Task',
            'description': 'Test description',
            'status': 'todo',
            'priority': 'medium',
            'due_date': '2025-12-31T23:59',
            'estimated_hours': 8,
            'assigned_to': [self.user.id],
            'team': self.team.id,
            'tags': [self.tag.id]
        })
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check task was created
        task = Task.objects.filter(title='Test Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.created_by, self.user)
        self.assertIn(self.user, task.assigned_to.all())
        self.assertEqual(task.team, self.team)
        self.assertIn(self.tag, task.tags.all())
        
    def test_task_detail_page(self):
        """Test task detail page displays correctly"""
        task = Task.objects.create(
            title='Test Task',
            description='Test description',
            due_date=timezone.now() + timedelta(days=7),
            created_by=self.user,
            team=self.team
        )
        TaskAssignment.objects.create(
            task=task,
            user=self.user,
            assigned_by=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/tasks/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'Test description')
        self.assertContains(response, 'Edit Task')
        
    def test_task_edit_page(self):
        """Test task edit page loads and works"""
        task = Task.objects.create(
            title='Test Task',
            description='Test description',
            due_date=timezone.now() + timedelta(days=7),
            created_by=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Test GET (load edit form)
        response = self.client.get(f'/tasks/tasks/{task.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Task')
        self.assertContains(response, task.title)
        
        # Test POST (update task)
        response = self.client.post(f'/tasks/tasks/{task.id}/edit/', {
            'title': 'Updated Task Title',
            'description': 'Updated description',
            'status': 'in_progress',
            'priority': 'high',
            'due_date': '2025-12-31T23:59',
            'estimated_hours': 10,
        })
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Check task was updated
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task Title')
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.priority, 'high')
        
    def test_task_permissions(self):
        """Test task edit permissions"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        task = Task.objects.create(
            title='Test Task',
            description='Test description',
            due_date=timezone.now() + timedelta(days=7),
            created_by=other_user
        )
        
        # Login as user who doesn't own the task
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(f'/tasks/tasks/{task.id}/edit/')
        # Should redirect with permission error
        self.assertEqual(response.status_code, 302)
        
    def test_task_filtering(self):
        """Test task filtering functionality"""
        # Create tasks with different statuses
        Task.objects.create(
            title='Todo Task',
            status='todo',
            due_date=timezone.now() + timedelta(days=7),
            created_by=self.user
        )
        Task.objects.create(
            title='In Progress Task', 
            status='in_progress',
            due_date=timezone.now() + timedelta(days=5),
            created_by=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Test status filter
        response = self.client.get('/tasks/tasks/?status=todo')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todo Task')
        self.assertNotContains(response, 'In Progress Task')
        
        # Test search
        response = self.client.get('/tasks/tasks/?search=Progress')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'In Progress Task')
        self.assertNotContains(response, 'Todo Task')
        
    def test_dashboard_statistics(self):
        """Test dashboard shows correct statistics"""
        # Create tasks assigned to user
        todo_task = Task.objects.create(
            title='Todo Task',
            status='todo',
            due_date=timezone.now() + timedelta(days=7),
            created_by=self.user
        )
        TaskAssignment.objects.create(
            task=todo_task,
            user=self.user,
            assigned_by=self.user
        )
        
        done_task = Task.objects.create(
            title='Done Task',
            status='done',
            due_date=timezone.now() + timedelta(days=3),
            created_by=self.user
        )
        TaskAssignment.objects.create(
            task=done_task,
            user=self.user,
            assigned_by=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tasks/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2')  # Total tasks
        self.assertContains(response, 'Statistics')
        
    def tearDown(self):
        """Clean up after tests"""
        # Re-enable logging
        logging.disable(logging.NOTSET)
