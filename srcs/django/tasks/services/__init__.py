"""
Task Services Package

Centralized business logic and services for task management.
Clear separation of concerns with improved naming.

- TaskCrudOperations: Core CRUD operations
- TaskQueryBuilder: Advanced query building and filtering  
- TaskFormAdapter: WEB form processing and pagination
- FormDataAdapter: Form data transformation utilities
"""

from .task_crud_operations import TaskCrudOperations
from .task_query_builder import TaskQueryBuilder
from .task_form_adapter import TaskFormAdapter
from .form_adapters import FormDataAdapter

__all__ = [
    'TaskCrudOperations', 
    'TaskQueryBuilder', 
    'TaskFormAdapter', 
    'FormDataAdapter'
]