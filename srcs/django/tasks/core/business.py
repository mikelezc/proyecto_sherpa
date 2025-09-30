"""
Task Business Operations

Unified interface for all task-related business logic.
Provides a clean facade to validation, calculation, metadata, and search operations.
"""

from .validations import TaskValidationUtils
from .calculations import TaskCalculationUtils
from .metadata import TaskMetadataUtils
from .search import (
    update_task_search_vector,
    update_all_search_vectors,
    rebuild_search_index
)

# Main business operation classes
__all__ = [
    'TaskValidationUtils',
    'TaskCalculationUtils', 
    'TaskMetadataUtils',
    'update_task_search_vector',
    'update_all_search_vectors',
    'rebuild_search_index',
    # Function aliases for convenience
    'validate_task_due_date',
    'validate_parent_task',
    'validate_metadata',
    'is_task_overdue',
    'calculate_task_progress',
    'ensure_default_metadata'
]

# Convenient function aliases
validate_task_due_date = TaskValidationUtils.validate_due_date
validate_parent_task = TaskValidationUtils.validate_parent_task
validate_metadata = TaskValidationUtils.validate_metadata
is_task_overdue = TaskCalculationUtils.is_task_overdue
calculate_task_progress = TaskCalculationUtils.calculate_progress_percentage
ensure_default_metadata = TaskMetadataUtils.ensure_default_metadata