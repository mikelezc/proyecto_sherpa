"""
Core business logic and utilities for the tasks application.

This module provides a clean, organized structure for all task-related business operations:

Primary Interface:
- business: Unified facade for all business operations

Specialized Modules:
- validations: Business rule validation utilities
- calculations: Task metrics and computational logic  
- metadata: Metadata management operations
- search: Full-text search functionality

Usage:
    from tasks.core.business import (
        TaskValidationUtils,
        TaskCalculationUtils,
        TaskMetadataUtils,
        is_task_overdue,
        validate_task_due_date
    )
"""