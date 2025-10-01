"""
Task Metadata Utilities

Specialized utilities for task metadata management and operations.
Handles default metadata structure, validation, and safe operations.
"""

from ..constants import DEFAULT_TASK_METADATA


class TaskMetadataUtils:
    """Utilities for task metadata operations"""
    
    @staticmethod
    def ensure_default_metadata(task):
        """Ensure task has default metadata structure"""
        if not task.metadata:
            task.metadata = DEFAULT_TASK_METADATA.copy()
            return
            
        # Ensure required keys exist by merging with defaults
        for key, default_value in DEFAULT_TASK_METADATA.items():
            if key not in task.metadata:
                if isinstance(default_value, dict):
                    task.metadata[key] = default_value.copy()
                elif isinstance(default_value, list):
                    task.metadata[key] = default_value.copy()
                else:
                    task.metadata[key] = default_value