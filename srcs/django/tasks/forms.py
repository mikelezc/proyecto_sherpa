"""
Django forms for task management
"""

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Task, Tag, Team
from .constants import TASK_STATUS_CHOICES, TASK_PRIORITY_CHOICES

User = get_user_model()


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority', 
            'due_date', 'estimated_hours', 'assigned_to', 'tags', 'team', 'parent_task'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the task...'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'assigned_to': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'team': forms.Select(attrs={'class': 'form-control'}),
            'parent_task': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional for better UX
        self.fields['team'].required = False
        self.fields['parent_task'].required = False
        self.fields['assigned_to'].required = False
        self.fields['tags'].required = False
        
        # Filter parent task options (exclude self and subtasks)
        if self.instance.pk:
            self.fields['parent_task'].queryset = Task.objects.exclude(
                Q(id=self.instance.pk) | Q(parent_task=self.instance.pk)
            )


class TaskFilterForm(forms.Form):
    """Form for filtering tasks in the list view"""
    
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


class CommentForm(forms.Form):
    """Form for adding comments to tasks"""
    
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add a comment...',
            'required': True
        }),
        label='Comment'
    )


class TaskAssignForm(forms.Form):
    """Form for assigning users to tasks"""
    
    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        
        # Filter users to show only team members if task has a team
        if task and task.team:
            user_queryset = task.team.members.all()
        else:
            user_queryset = User.objects.filter(is_active=True)
        
        self.fields['users'] = forms.ModelMultipleChoiceField(
            queryset=user_queryset,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            required=False,
            label='Assign to users'
        )
