#!/usr/bin/env python3
import os
import sys
import time
import socket
import logging
import django
from django.core.management import execute_from_command_line

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")


def wait_for_db(host='db', port=5432, max_retries=30):
    """Wait for the database service to be available"""
    logger.info(f"Waiting for database at {host}:{port} to be ready...")
    
    for attempt in range(max_retries):
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info("✅ Database is ready!")
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            if attempt == max_retries - 1:
                logger.error("❌ Could not connect to database after multiple attempts")
                return False
            logger.info(f"⏳ Database not ready, attempt {attempt + 1}/{max_retries}, waiting 2 seconds...")
            time.sleep(2)
    
    return False


def wait_for_redis(host='redis', port=6379, max_retries=30):
    """Wait for Redis service to be available"""
    logger.info(f"Waiting for Redis at {host}:{port} to be ready...")
    
    for attempt in range(max_retries):
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info("✅ Redis is ready!")
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            if attempt == max_retries - 1:
                logger.error("❌ Could not connect to Redis after multiple attempts")
                return False
            logger.info(f"⏳ Redis not ready, attempt {attempt + 1}/{max_retries}, waiting 2 seconds...")
            time.sleep(2)
    
    return False


def run_django_command(command):
    """Run a Django management command"""
    try:
        logger.info(f"🔧 Running Django command: {' '.join(command)}")
        execute_from_command_line(command)
        return True
    except Exception as e:
        logger.error(f"❌ Error running Django command {' '.join(command)}: {e}")
        return False


def setup_django():
    """Setup Django application"""
    logger.info("🚀 Setting up Django application...")
    
    # Setup Django
    django.setup()
    
    # Create migrations for apps
    if not run_django_command(['manage.py', 'makemigrations']):
        logger.warning("⚠️ No new migrations to create")
    
    # Run migrations
    if not run_django_command(['manage.py', 'migrate']):
        logger.error("❌ Failed to run migrations")
        return False
    
    # Collect static files (if needed)
    if not run_django_command(['manage.py', 'collectstatic', '--noinput']):
        logger.warning("⚠️ Failed to collect static files (this might be normal)")
    
    # Create superuser if specified in environment
    if os.environ.get('DJANGO_SUPERUSER_USERNAME'):
        logger.info("👤 Creating Django superuser...")
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME')).exists():
                run_django_command([
                    'manage.py', 'createsuperuser', '--noinput',
                    '--username', os.environ.get('DJANGO_SUPERUSER_USERNAME'),
                    '--email', os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
                ])
        except Exception as e:
            logger.warning(f"⚠️ Could not create superuser: {e}")
    
    # Load seed data if environment variable is set
    if os.environ.get('LOAD_SEED_DATA', 'False').lower() == 'true':
        logger.info("🌱 Loading seed data...")
        if not run_django_command(['manage.py', 'seed_data']):
            logger.warning("⚠️ Failed to load seed data (might be normal if data already exists)")
        else:
            logger.info("✅ Seed data loaded successfully!")
            # Update search vectors for seeded tasks
            if not run_django_command(['manage.py', 'update_search_vectors']):
                logger.warning("⚠️ Failed to update search vectors")
    
    # Setup periodic task descriptions for Django Admin
    logger.info("📋 Setting up periodic task descriptions...")
    run_django_command(['manage.py', 'setup_periodic_task_descriptions', '--quiet-missing'])
    logger.info("✅ Periodic task descriptions configured!")
    
    logger.info("✅ Django setup completed!")
    return True


def start_server():
    """Start the Django development server"""
    logger.info("🌐 Starting Django development server...")
    
    try:
        # For development, use runserver
        if os.environ.get('DEBUG', 'False').lower() == 'true':
            logger.info("🔧 Starting in DEBUG mode with runserver")
            os.execvp('python', ['python', 'manage.py', 'runserver', '0.0.0.0:8000'])
        else:
            # For production, you might want to use gunicorn
            logger.info("🔧 Starting in production mode with gunicorn")
            os.execvp('gunicorn', [
                'gunicorn',
                '--bind', '0.0.0.0:8000',
                '--workers', '3',
                '--timeout', '120',
                'main.wsgi:application'
            ])
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


def main():
    """Main entrypoint function"""
    logger.info("🚀 Starting Django entrypoint...")
    
    # Wait for dependencies
    if not wait_for_db():
        logger.error("❌ Database is not available")
        sys.exit(1)
    
    if not wait_for_redis():
        logger.error("❌ Redis is not available")
        sys.exit(1)
    
    # Setup Django
    if not setup_django():
        logger.error("❌ Django setup failed")
        sys.exit(1)
    
    # Start the server
    start_server()


if __name__ == "__main__":
    main()
