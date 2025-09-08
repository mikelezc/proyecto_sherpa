"""
Django admin configuration for task management
"""

from django.contrib import admin
from .models import Task, Comment, Tag, Team, TaskHistory, TaskAssignment, TimeLog, TaskTemplate


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    filter_horizontal = ['members']


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'estimated_hours', 'created_by', 'is_active']
    search_fields = ['name', 'title_template']
    list_filter = ['priority', 'is_active', 'created_at']
    filter_horizontal = ['tags']


class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 0
    readonly_fields = ['assigned_at']


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class TimeLogInline(admin.TabularInline):
    model = TimeLog
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status', 'priority', 'created_by', 'due_date', 
        'is_overdue', 'estimated_hours', 'actual_hours', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'is_overdue', 'is_archived', 
        'created_at', 'due_date', 'team'
    ]
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    filter_horizontal = ['tags']
    inlines = [TaskAssignmentInline, CommentInline, TimeLogInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Timeline', {
            'fields': ('due_date', 'estimated_hours', 'actual_hours')
        }),
        ('Organization', {
            'fields': ('team', 'tags', 'parent_task', 'template')
        }),
        ('Metadata', {
            'fields': ('metadata', 'is_archived'),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_overdue'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'created_by', 'team', 'parent_task'
        )


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'assigned_by', 'is_primary', 'assigned_at']
    list_filter = ['is_primary', 'assigned_at']
    search_fields = ['task__title', 'user__username', 'assigned_by__username']
    readonly_fields = ['assigned_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at', 'is_edited']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['task__title', 'author__username', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['task__title', 'user__username']
    readonly_fields = ['timestamp']

    def has_add_permission(self, request):
        # History entries should only be created automatically
        return False

    def has_change_permission(self, request, obj=None):
        # History entries should not be editable
        return False


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'hours', 'date_logged', 'created_at']
    list_filter = ['date_logged', 'created_at']
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['created_at']
