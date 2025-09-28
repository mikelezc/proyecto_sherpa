"""
Django admin configuration for task management system

This module configures administrative interfaces for all task models.
"""

from django.contrib import admin
from .models import Task, Comment, Tag, Team, TaskHistory, TaskAssignment


# ========== SIMPLE CONFIGURATIONS ==========
# These are basic configurations for models that only need lists and filters

@admin.register(Tag)  # Tags for categorizing tasks
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Team)  # Teams that can be assigned to tasks
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    # Special widget for visually selecting multiple members
    filter_horizontal = ['members']


# ========== INLINES (Sub-forms) ==========
# These allow editing related models directly from the main Task page

class TaskAssignmentInline(admin.TabularInline):
    """Allows assigning users to tasks directly from Task page"""
    model = TaskAssignment
    extra = 0
    readonly_fields = ['assigned_at']


class CommentInline(admin.TabularInline):
    """Allows adding comments directly from Task page"""
    model = Comment
    extra = 0
    readonly_fields = ['created_at']


# ========== MAIN CONFIGURATION: TaskAdmin ==========
# This is the most complex and important configuration in the system

@admin.register(Task)  # Main task model (most complex)
class TaskAdmin(admin.ModelAdmin):
    """
    Advanced configuration for Task administration with:
    - List display with optimized queries
    - Advanced filtering and search  
    - Inline editing of assignments and comments
    - Bulk actions for common operations
    """
    
    # What to display in the list view
    list_display = [
        'title', 'status', 'priority', 'due_date', 'created_by',
        'is_overdue', 'estimated_hours', 'created_at'
    ]
    
    # What fields can be searched
    search_fields = ['title', 'description', 'created_by__username']
    
    # Sidebar filters
    list_filter = [
        'status', 'priority', 'is_overdue', 'is_archived',
        'created_at', 'due_date', 'team'
    ]
    
    # Fields that can be edited directly in list view  
    list_editable = ['status', 'priority']
    
    # Default ordering (most recent first)
    ordering = ['-created_at']
    
    # How many per page
    list_per_page = 50
    
    # Inline forms (edit related models on same page)
    inlines = [TaskAssignmentInline, CommentInline]
    
    # Optimize database queries (reduces queries from N+1 to 2)
    list_select_related = ['created_by', 'team']
    list_prefetch_related = ['assigned_to', 'tags']
    
    # Group fields in the edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Timeline', {
            'fields': ('due_date', 'estimated_hours', 'actual_hours'),
            'classes': ('collapse',)
        }),
        ('Relationships', {
            'fields': ('team', 'parent_task', 'tags'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'is_archived'),
            'classes': ('collapse',)
        })
    )
    
    # Multiple selection widget for many-to-many fields
    filter_horizontal = ['tags']
    
    # Read-only fields (calculated or auto-set)
    readonly_fields = ['created_at', 'updated_at', 'is_overdue', 'search_vector']
    
    # Custom bulk actions
    actions = ['mark_as_todo', 'mark_as_completed', 'archive_tasks']
    
    def mark_as_todo(self, request, queryset):
        """Bulk action to mark selected tasks as todo"""
        count = queryset.update(status='todo')
        self.message_user(request, f"{count} tasks marked as Todo")
    mark_as_todo.short_description = "Mark selected tasks as Todo"
    
    def mark_as_completed(self, request, queryset):
        """Bulk action to mark selected tasks as completed"""
        count = queryset.update(status='done')
        self.message_user(request, f"{count} tasks marked as Completed")
    mark_as_completed.short_description = "Mark selected tasks as Completed"
    
    def archive_tasks(self, request, queryset):
        """Bulk action to archive selected tasks"""
        count = queryset.update(is_archived=True)
        self.message_user(request, f"{count} tasks archived")
    archive_tasks.short_description = "Archive selected tasks"


# ========== SECONDARY CONFIGURATIONS ==========

@admin.register(Comment)  # Comments on tasks
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at', 'is_edited']
    search_fields = ['content', 'author__username', 'task__title']
    list_filter = ['is_edited', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


# TaskHistory is CRITICAL for traceability and auditing

@admin.register(TaskHistory)  # Change history (READ ONLY)
class TaskHistoryAdmin(admin.ModelAdmin):
    """
    READ-ONLY admin for task history - DO NOT allow editing
    This maintains audit trail integrity
    """
    list_display = ['task', 'user', 'action', 'timestamp']
    search_fields = ['task__title', 'user__username', 'action']
    list_filter = ['action', 'timestamp']
    readonly_fields = ['task', 'user', 'action', 'changes', 'timestamp']
    
    # Prevent any modifications to maintain audit integrity
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TaskAssignment)  # Task-User assignments
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'assigned_by', 'assigned_at', 'is_primary']
    search_fields = ['task__title', 'user__username', 'assigned_by__username']
    list_filter = ['is_primary', 'assigned_at']
    readonly_fields = ['assigned_at']


# ========== ADMIN SITE CUSTOMIZATION ==========
# Customize the admin site header and title

admin.site.site_header = "Task Management Administration"
admin.site.site_title = "Task Management Admin"
admin.site.index_title = "Welcome to Task Management System"


"""
QUICK REFERENCE:

Django automatically imports this file and registers all models decorated with @admin.register()
Accessible at: http://localhost:8000/admin/ with superuser credentials

KEY FEATURES:
- Optimized queries (select_related, prefetch_related)
- Bulk actions for common operations  
- Inline editing of related models
- Advanced filtering and search
- Read-only audit trail (TaskHistory)
- Customizable field grouping
"""