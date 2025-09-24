"""
Django admin configuration for task management

This file configures administrative interfaces for all task models.
Django automatically imports this file and registers all models decorated with @admin.register()
Accessible at: http://localhost:8080/admin/ with user demo_admin/demo123 (SUPERUSER)
"""

from django.contrib import admin
from .models import Task, Comment, Tag, Team, TaskHistory, TaskAssignment, TimeLog, TaskTemplate


# ========== SIMPLE CONFIGURATIONS ==========
# These are basic configurations for models that only need lists and filters

@admin.register(Tag)  # Automatically registers Tag in admin
class TagAdmin(admin.ModelAdmin):
    # Columns displayed in the main list
    list_display = ['name', 'color', 'created_at']
    # Fields available for search (search box appears)
    search_fields = ['name']
    # Sidebar filters to filter by date
    list_filter = ['created_at']


@admin.register(Team)  # Automatically registers Team in admin
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name', 'description']  # Search by name and description
    list_filter = ['created_at']
    # Special widget for visually selecting multiple members
    filter_horizontal = ['members']


@admin.register(TaskTemplate)  # Automatically registers TaskTemplate in admin
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'estimated_hours', 'created_by', 'is_active']
    search_fields = ['name', 'title_template']
    list_filter = ['priority', 'is_active', 'created_at']  # Multiple filters
    # Horizontal widget for tags (easier to use than multiple select)
    filter_horizontal = ['tags']


# ========== INLINES (Sub-forms) ==========
# These allow editing related models directly from the main Task page

class TaskAssignmentInline(admin.TabularInline):
    """Allows managing assignments directly from Task page"""
    model = TaskAssignment
    extra = 0  # Don't create empty rows by default
    readonly_fields = ['assigned_at']  # Non-editable field


class CommentInline(admin.TabularInline):
    """Allows adding/editing comments directly from Task page"""
    model = Comment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']  # System fields not editable


class TimeLogInline(admin.TabularInline):
    """Allows logging work time directly from Task page"""
    model = TimeLog
    extra = 0
    readonly_fields = ['created_at']


# ========== MAIN CONFIGURATION: TaskAdmin ==========
# This is the most complex and important configuration in the system

@admin.register(Task)  # Automatically registers Task in admin
class TaskAdmin(admin.ModelAdmin):
    # ===== LIST VIEW (what you see in /admin/tasks/task/) =====
    list_display = [
        'title', 'status', 'priority', 'created_by', 'due_date', 
        'is_overdue', 'estimated_hours', 'actual_hours', 'created_at'
    ]  # Columns that appear in the main table
    
    # Sidebar filters (right sidebar)
    list_filter = [
        'status', 'priority', 'is_overdue', 'is_archived', 
        'created_at', 'due_date', 'team'
    ]
    
    # Search fields (top search box)
    # created_by__username allows searching by creator's name
    search_fields = ['title', 'description', 'created_by__username']
    
    # Fields that cannot be edited (appear grayed out)
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    
    # Horizontal widget for tags (more user-friendly)
    filter_horizontal = ['tags']
    
    # ===== INTEGRATED SUB-FORMS =====
    # These appear on the same page when editing a Task
    inlines = [TaskAssignmentInline, CommentInline, TimeLogInline]
    
    # ===== FORM ORGANIZATION =====
    # Divides the form into organized collapsible sections
    fieldsets = (
        ('Basic Information', {  # Always visible section
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Timeline', {  # Temporal information
            'fields': ('due_date', 'estimated_hours', 'actual_hours')
        }),
        ('Organization', {  # Organization and hierarchy
            'fields': ('team', 'tags', 'parent_task', 'template')
        }),
        ('Metadata', {  # Additional information (collapsed by default)
            'fields': ('metadata', 'is_archived'),
            'classes': ('collapse',)  # Appears collapsed
        }),
        ('System Fields', {  # System fields (collapsed by default)
            'fields': ('created_by', 'created_at', 'updated_at', 'is_overdue'),
            'classes': ('collapse',),  # Appears collapsed
        }),
    )

    # ===== PERFORMANCE OPTIMIZATION =====
    # Avoids N+1 query problem by loading relations at once
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'created_by', 'team', 'parent_task'  # Load these relations in single query
        )


# ========== SECONDARY ADMINISTRATIONS ==========
# These are for managing related models separately

@admin.register(TaskAssignment)  # Independent assignment management
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'assigned_by', 'is_primary', 'assigned_at']
    list_filter = ['is_primary', 'assigned_at']
    # Cross search: searches in task title and usernames
    search_fields = ['task__title', 'user__username', 'assigned_by__username']
    readonly_fields = ['assigned_at']  # Date is assigned automatically


@admin.register(Comment)  # Comment moderation
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at', 'is_edited']
    list_filter = ['is_edited', 'created_at']  # Filter edited comments
    search_fields = ['task__title', 'author__username', 'content']  # Search in content
    readonly_fields = ['created_at', 'updated_at']


# ========== AUDITING AND COMPLIANCE ==========
# TaskHistory is CRITICAL for traceability and auditing

@admin.register(TaskHistory)  # Change history (READ ONLY)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']  # Filter by action type
    search_fields = ['task__title', 'user__username']
    readonly_fields = ['timestamp']

    # ===== SECURITY RESTRICTIONS =====
    # History must NOT be modifiable to maintain integrity
    def has_add_permission(self, request):
        # History entries should only be created automatically
        return False  # ❌ Cannot create entries manually

    def has_change_permission(self, request, obj=None):
        # History entries should not be editable
        return False  # ❌ Cannot edit existing entries


@admin.register(TimeLog)  # Work hours tracking
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'hours', 'date_logged', 'created_at']
    list_filter = ['date_logged', 'created_at']  # Filter by dates
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['created_at']


# ========== HOW EVERYTHING WORKS ==========
"""
Django automatically:
1. Imports this file when it starts (because tasks is in INSTALLED_APPS)
2. Processes all @admin.register() and registers the models
3. Applies all configurations (fieldsets, inlines, permissions, etc.)
4. Makes everything available at http://localhost:8080/admin/

Access:
- URL: http://localhost:8080/admin/
- User: demo_admin 
- Password: demo123
- (Created automatically by seeder in seed_data.py as SUPERUSER)

Result: 8 fully manageable models with professional interfaces
"""
