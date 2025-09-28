"""
Django settings for task management system project.
Enterprise-focused configuration for authentication and task management.
"""

from django.core.management.utils import get_random_secret_key
from pathlib import Path
from datetime import timedelta
import logging
import os

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    logger.warning("DJANGO_SECRET_KEY environment variable not set, generating random key")
    SECRET_KEY = get_random_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["*"] if DEBUG else ["localhost", "127.0.0.1"]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",  # PostgreSQL extensions
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
]

LOCAL_APPS = [
    "main",  # Main app for management commands
    "authentication",
    "tasks",  # New task management app
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "main.middleware.APICsrfExemptMiddleware",  # Custom CSRF middleware for APIs
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "authentication.middleware.UserSessionMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "authentication" / "web" / "templates",
            BASE_DIR / "tasks" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("POSTGRES_DB", "task_management_db"),
        "USER": os.environ.get("POSTGRES_USER", "admin"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "db"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
        "OPTIONS": {
            "connect_timeout": 30,
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "authentication.CustomUser"

# Login/logout URLs
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "task_list"
LOGOUT_REDIRECT_URL = "login"

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# CSRF settings for APIs
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Exempt API endpoints from CSRF
CSRF_EXEMPT_URLS = [
    r'api/tasks/',    # Tasks API - remove leading slash
    r'api/auth/',     # Authentication API  
    r'api/users/',    # Users API
]

# Celery Configuration
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Configuration
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Periodic tasks (crontab of tasks)
CELERY_BEAT_SCHEDULE = {
    "cleanup-inactive-users": {
        "task": "authentication.tasks.cleanup_inactive_users",
        "schedule": 300.0,  # Every 5 minutes for demo
    },
    "check-overdue-tasks": {
        "task": "tasks.infrastructure.celery_tasks.check_overdue_tasks",
        "schedule": 3600.0,  # Every hour
    },
    "generate-daily-summary": {
        "task": "tasks.infrastructure.celery_tasks.generate_daily_summary",
        "schedule": 86400.0,  # Every day
    },
    "cleanup-archived-tasks": {
        "task": "tasks.infrastructure.celery_tasks.cleanup_archived_tasks",
        "schedule": 604800.0,  # Every week (7 days * 24 hours * 60 minutes * 60 seconds)
    },
    "weekly-search-maintenance": {
        "task": "tasks.infrastructure.celery_tasks.weekly_search_maintenance",
        "schedule": 604800.0,  # Every week (7 days * 24 hours * 60 minutes * 60 seconds)
    },
}

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# Testing configuration
TEST_RUNNER = 'main.test_runner.ColoredTestRunner'

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@taskmanagement.com")

# User activity settings
TEST_MODE = os.environ.get("TEST_MODE", "False").lower() == "true"
TIME_MULTIPLIER = 86400 if not TEST_MODE else 1  # seconds in a day or 1 for testing

# Inactivity settings
if TEST_MODE:
    EMAIL_VERIFICATION_TIMEOUT = 10
    INACTIVITY_WARNING = 40
    INACTIVITY_THRESHOLD = 60
    TASK_CHECK_INTERVAL = 5
    SESSION_ACTIVITY_CHECK = 2
else:
    EMAIL_VERIFICATION_TIMEOUT = 600  # 10 minutes
    INACTIVITY_WARNING = 53 * TIME_MULTIPLIER  # 53 days
    INACTIVITY_THRESHOLD = 60 * TIME_MULTIPLIER  # 60 days
    TASK_CHECK_INTERVAL = 600  # 10 minutes
    SESSION_ACTIVITY_CHECK = 300  # 5 minutes

# Session settings
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = INACTIVITY_THRESHOLD * 2

# Security settings
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "authentication": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "tasks": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# JWT Configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_LIFETIME = timedelta(minutes=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME", "15")))
JWT_REFRESH_TOKEN_LIFETIME = timedelta(days=int(os.environ.get("JWT_REFRESH_TOKEN_LIFETIME", "7")))

# Site configuration
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")
