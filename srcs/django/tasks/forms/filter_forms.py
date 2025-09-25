"""
Filter Forms - Task filtering and search forms

Shared filtering forms compatible with both API and WEB interfaces.
"""

from django import forms
from ..constants import TASK_STATUS_CHOICES, TASK_PRIORITY_CHOICES


class TaskFilterForm(forms.Form):
    """Form for filtering tasks - unified for API and WEB usage"""
    
    STATUS_CHOICES = [('', 'All Statuses')] + TASK_STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'All Priorities')] + TASK_PRIORITY_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search tasks...',
            'type': 'search'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def get_filter_params(self):
        """Convert form data to filter parameters compatible with TaskFilter"""
        if not self.is_valid():
            return {}
        
        params = {}
        if self.cleaned_data.get('search'):
            params['search'] = self.cleaned_data['search']
        if self.cleaned_data.get('status'):
            params['status'] = self.cleaned_data['status']
        if self.cleaned_data.get('priority'):
            params['priority'] = self.cleaned_data['priority']
        if self.cleaned_data.get('assigned_to_me'):
            params['assigned_to_me'] = self.cleaned_data['assigned_to_me']
        
        return params