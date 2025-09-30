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
    
    @staticmethod
    def get_metadata_value(task, key, default=None):
        """Safely get a metadata value with fallback"""
        if not task.metadata:
            return default
        return task.metadata.get(key, default)
    
    @staticmethod
    def set_metadata_value(task, key, value):
        """Safely set a metadata value"""
        if not task.metadata:
            task.metadata = {}
        task.metadata[key] = value
    
    @staticmethod
    def update_metadata(task, updates):
        """Update multiple metadata values at once"""
        if not task.metadata:
            task.metadata = {}
        task.metadata.update(updates)
    
    @staticmethod
    def validate_metadata_structure(metadata):
        """Validate metadata structure matches expected schema"""
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        
        # Check for required top-level keys from defaults
        required_keys = set(DEFAULT_TASK_METADATA.keys())
        metadata_keys = set(metadata.keys())
        
        missing_keys = required_keys - metadata_keys
        if missing_keys:
            return False, f"Missing required metadata keys: {list(missing_keys)}"
        
        return True, "Valid metadata structure"
    
    @staticmethod
    def reset_metadata(task):
        """Reset task metadata to default structure"""
        task.metadata = DEFAULT_TASK_METADATA.copy()
    
    @staticmethod
    def merge_metadata(task, new_metadata):
        """Merge new metadata with existing, preserving structure"""
        if not task.metadata:
            task.metadata = DEFAULT_TASK_METADATA.copy()
        
        for key, value in new_metadata.items():
            if key in task.metadata and isinstance(task.metadata[key], dict) and isinstance(value, dict):
                task.metadata[key].update(value)
            else:
                task.metadata[key] = value