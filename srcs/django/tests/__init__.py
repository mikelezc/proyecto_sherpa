"""
Test configuration and base classes for the task management system
"""
import os
import django
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import tempfile

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup for all tests"""
    
    def setUp(self):
        """Set up test data"""
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

    def tearDown(self):
        """Clean up after tests"""
        User.objects.all().delete()


class BaseAPITestCase(APITestCase):
    """Base API test case with authentication setup"""
    
    def setUp(self):
        """Set up test data and API client"""
        self.client = APIClient()
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

    def authenticate_user(self, user=None):
        """Authenticate a user for API testing"""
        if user is None:
            user = self.user
        self.client.force_authenticate(user=user)

    def tearDown(self):
        """Clean up after tests"""
        User.objects.all().delete()


class BaseIntegrationTestCase(TransactionTestCase):
    """Base integration test case for testing across multiple services"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='integrationuser',
            email='integration@example.com',
            password='integrationpass123'
        )

    def tearDown(self):
        """Clean up after integration tests"""
        User.objects.all().delete()
