"""
Task Constants and Choices

Centralized location for all task-related constants, choices, and enums.
Separates static definitions from model structure.
"""

# Task Status Choices
TASK_STATUS_CHOICES = [
    ('todo', 'To Do'),
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('review', 'In Review'),
    ('done', 'Done'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

# Task Priority Choices
TASK_PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

# Task History Action Choices
TASK_HISTORY_ACTION_CHOICES = [
    ('created', 'Created'),
    ('updated', 'Updated'),
    ('assigned', 'Assigned'),
    ('unassigned', 'Unassigned'),
    ('status_changed', 'Status Changed'),
    ('archived', 'Archived'),
    ('unarchived', 'Unarchived'),
]

# Status Progress Mapping for Calculations
TASK_STATUS_PROGRESS = {
    'todo': 0,
    'pending': 10,
    'in_progress': 50,
    'review': 80,
    'done': 100,
    'completed': 100,
    'cancelled': 0
}

# Completed Statuses
COMPLETED_STATUSES = ['done', 'completed']

# Active Statuses (not completed or cancelled)
ACTIVE_STATUSES = ['todo', 'pending', 'in_progress', 'review']

# Default Colors
DEFAULT_TAG_COLOR = "#007bff"
DEFAULT_TEAM_COLOR = "#6c757d"

# Metadata Defaults
DEFAULT_TASK_METADATA = {
    'labels': [],
    'external_refs': {},
    'settings': {
        'notifications': True,
        'auto_assign': False
    }
}

# Database Constants
MAX_TASK_TITLE_LENGTH = 200
MAX_TAG_NAME_LENGTH = 50
MAX_TEAM_NAME_LENGTH = 100
MAX_PRIORITY_LENGTH = 20
MAX_STATUS_LENGTH = 20
MAX_ACTION_LENGTH = 20
MAX_COLOR_LENGTH = 7  # For hex colors like #ffffff

# Decimal Field Settings
HOURS_MAX_DIGITS = 6
HOURS_DECIMAL_PLACES = 2