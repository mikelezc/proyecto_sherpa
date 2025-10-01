"""
Form Adapters - Utilities for converting form data to service objects

Contains helper classes and utilities for transforming Django form data
into format compatible with service layer operations.
"""


class FormDataAdapter:
    """Adapter class to convert Django form cleaned_data to service-compatible format"""
    
    def __init__(self, cleaned_data):
        """Initialize adapter with form's cleaned_data"""
        # Set all basic fields as attributes
        for key, value in cleaned_data.items():
            setattr(self, key, value)
        
        # Handle many-to-many fields - convert to ID lists
        if 'assigned_to' in cleaned_data:
            self.assigned_to_ids = [user.id for user in cleaned_data['assigned_to']]
            
        if 'tags' in cleaned_data:
            self.tag_ids = [tag.id for tag in cleaned_data['tags']]
        
        # Handle foreign key fields that need _id suffix
        if 'team' in cleaned_data and cleaned_data['team']:
            self.team_id = cleaned_data['team'].id
            
        if 'parent_task' in cleaned_data and cleaned_data['parent_task']:
            self.parent_task_id = cleaned_data['parent_task'].id
    
    @classmethod
    def from_form(cls, form):
        """Create adapter from Django form instance"""
        return cls(form.cleaned_data)
    
    def __repr__(self):
        """String representation for debugging"""
        attrs = [f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith('_')]
        return f"FormDataAdapter({', '.join(attrs)})"