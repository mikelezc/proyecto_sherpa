"""
Unit tests for core models
Testing all model functionality, validations, and business logic
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, Comment, Tag, Team, TaskHistory
from decimal import Decimal

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def test_create_user(self):
        """Test user creation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test superuser creation"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_username_unique(self):
        """Test username uniqueness constraint"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_email_validation(self):
        """Test email validation"""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        with self.assertRaises(ValidationError):
            user = User(**invalid_data)
            user.full_clean()


class TaskModelTest(TestCase):
    """Test cases for Task model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='taskuser',
            email='task@example.com',
            password='taskpass123'
        )
        self.assignee = User.objects.create_user(
            username='assignee',
            email='assignee@example.com',
            password='assigneepass123'
        )
        self.tag = Tag.objects.create(name='urgent', color='#ff0000')
        
        self.task_data = {
            'title': 'Test Task',
            'description': 'This is a test task',
            'status': 'pending',
            'priority': 'high',
            'due_date': timezone.now() + timedelta(days=7),
            'estimated_hours': Decimal('8.0'),
            'created_by': self.user
        }

    def test_create_task(self):
        """Test task creation"""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.created_by, self.user)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
        self.assertFalse(task.is_archived)

    def test_task_str_representation(self):
        """Test task string representation"""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(str(task), 'Test Task')

    def test_task_assignment(self):
        """Test task assignment to users"""
        task = Task.objects.create(**self.task_data)
        # Use the through model TaskAssignment instead of direct add
        from tasks.models import TaskAssignment
        TaskAssignment.objects.create(
            task=task,
            user=self.assignee,
            assigned_by=self.user
        )
        self.assertIn(self.assignee, task.assigned_to.all())
        self.assertEqual(task.assigned_to.count(), 1)

    def test_task_tags(self):
        """Test task tag assignment"""
        task = Task.objects.create(**self.task_data)
        task.tags.add(self.tag)
        self.assertIn(self.tag, task.tags.all())
        self.assertEqual(task.tags.count(), 1)

    def test_task_validation(self):
        """Test task field validations"""
        # Test invalid status
        invalid_data = self.task_data.copy()
        invalid_data['status'] = 'invalid_status'
        with self.assertRaises(ValidationError):
            task = Task(**invalid_data)
            task.full_clean()

    def test_task_metadata(self):
        """Test task metadata JSONField"""
        metadata = {'custom_field': 'value', 'priority_score': 95}
        task_data = self.task_data.copy()
        task_data['metadata'] = metadata
        task = Task.objects.create(**task_data)
        self.assertEqual(task.metadata['custom_field'], 'value')
        self.assertEqual(task.metadata['priority_score'], 95)

    def test_subtask_relationship(self):
        """Test parent-child task relationships"""
        parent_task = Task.objects.create(**self.task_data)
        child_data = self.task_data.copy()
        child_data['title'] = 'Child Task'
        child_data['parent_task'] = parent_task
        child_task = Task.objects.create(**child_data)
        
        self.assertEqual(child_task.parent_task, parent_task)
        self.assertIn(child_task, parent_task.subtasks.all())


class CommentModelTest(TestCase):
    """Test cases for Comment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='commentuser',
            email='comment@example.com',
            password='commentpass123'
        )
        self.task = Task.objects.create(
            title='Task for Comments',
            description='A task to test comments',
            status='pending',
            priority='medium',
            due_date=timezone.now() + timedelta(days=5),
            estimated_hours=Decimal('4.0'),
            created_by=self.user
        )

    def test_create_comment(self):
        """Test comment creation"""
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,  # Changed from 'user' to 'author'
            content='This is a test comment'
        )
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.task, self.task)
        self.assertEqual(comment.author, self.user)  # Changed from 'user' to 'author'
        self.assertIsNotNone(comment.created_at)

    def test_comment_str_representation(self):
        """Test comment string representation"""
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,  # Changed from 'user' to 'author'
            content='Test comment'
        )
        expected = f"Comment by {self.user.username} on {self.task.title}"
        self.assertEqual(str(comment), expected)


class TagModelTest(TestCase):
    """Test cases for Tag model"""
    
    def test_create_tag(self):
        """Test tag creation"""
        tag = Tag.objects.create(name='priority', color='#ff9900')
        self.assertEqual(tag.name, 'priority')
        self.assertEqual(tag.color, '#ff9900')

    def test_tag_str_representation(self):
        """Test tag string representation"""
        tag = Tag.objects.create(name='urgent', color='#ff0000')
        self.assertEqual(str(tag), 'urgent')

    def test_tag_name_unique(self):
        """Test tag name uniqueness"""
        Tag.objects.create(name='duplicate', color='#000000')
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name='duplicate', color='#ffffff')


class TeamModelTest(TestCase):
    """Test cases for Team model"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='teamuser1',
            email='team1@example.com',
            password='teampass123'
        )
        self.user2 = User.objects.create_user(
            username='teamuser2',
            email='team2@example.com',
            password='teampass123'
        )

    def test_create_team(self):
        """Test team creation"""
        team = Team.objects.create(
            name='Development Team',
            description='Main development team',
            created_by=self.user1  # Added required field
        )
        self.assertEqual(team.name, 'Development Team')
        self.assertEqual(team.description, 'Main development team')

    def test_team_members(self):
        """Test team member management"""
        team = Team.objects.create(name='Test Team', created_by=self.user1)  # Added required field
        team.members.add(self.user1, self.user2)
        
        self.assertEqual(team.members.count(), 2)
        self.assertIn(self.user1, team.members.all())
        self.assertIn(self.user2, team.members.all())

    def test_team_str_representation(self):
        """Test team string representation"""
        team = Team.objects.create(name='QA Team', created_by=self.user1)  # Added required field
        self.assertEqual(str(team), 'QA Team')


class TaskHistoryModelTest(TestCase):
    """Test cases for TaskHistory model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='historyuser',
            email='history@example.com',
            password='historypass123'
        )
        self.task = Task.objects.create(
            title='Task for History',
            description='A task to test history',
            status='pending',
            priority='low',
            due_date=timezone.now() + timedelta(days=3),
            estimated_hours=Decimal('2.0'),
            created_by=self.user
        )

    def test_create_task_history(self):
        """Test task history creation"""
        history = TaskHistory.objects.create(
            task=self.task,
            user=self.user,
            action='created',
            changes={'status': {'old': '', 'new': 'pending'}}  # Use JSONField format
        )
        self.assertEqual(history.task, self.task)
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.action, 'created')
        self.assertEqual(history.changes['status']['new'], 'pending')

    def test_history_str_representation(self):
        """Test task history string representation"""
        history = TaskHistory.objects.create(
            task=self.task,
            user=self.user,
            action='updated',
            changes={'priority': {'old': 'low', 'new': 'high'}}  # Use JSONField format
        )
        expected = f"updated by {self.user.username} on {self.task.title}"
        self.assertEqual(str(history), expected)
