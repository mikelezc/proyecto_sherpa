"""
Task Serializers

Serialization functions for converting model instances to API schemas.
Shared between API and WEB interfaces for consistent data representation.
"""

from ..api.schemas import (
    UserMinimalSchema,
    TagSchema, 
    TeamSchema,
    TaskAssignmentSchema,
    CommentSchema,
    TaskListSchema,
    TaskDetailSchema,
    TaskHistorySchema
)


def serialize_user_minimal(user):
    """Serialize user to minimal schema for API responses"""
    return UserMinimalSchema(
        id=user.id,
        username=user.username,
        email=user.email
    )


def serialize_tag(tag):
    """Serialize tag model to API schema"""
    return TagSchema(
        id=tag.id,
        name=tag.name,
        color=tag.color
    )


def serialize_team(team):
    """Serialize team model to API schema"""
    return TeamSchema(
        id=team.id,
        name=team.name
    )


def serialize_assignment(assignment):
    """Serialize task assignment model to API schema"""
    return TaskAssignmentSchema(
        id=assignment.id,
        user=serialize_user_minimal(assignment.user),
        assigned_at=assignment.assigned_at,
        assigned_by=serialize_user_minimal(assignment.assigned_by),
        is_primary=assignment.is_primary
    )


def serialize_comment(comment):
    """Serialize comment model to API schema"""
    return CommentSchema(
        id=comment.id,
        content=comment.content,
        author=serialize_user_minimal(comment.author),
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_edited=comment.is_edited
    )


def serialize_task_list(task):
    """Serialize task model for list view API responses"""
    return TaskListSchema(
        id=task.id,
        title=task.title,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        created_by=serialize_user_minimal(task.created_by),
        assigned_to=[serialize_user_minimal(user) for user in task.assigned_to.all()],
        tags=[serialize_tag(tag) for tag in task.tags.all()],
        created_at=task.created_at,
        is_overdue=task.is_past_due
    )


def serialize_task_detail(task):
    """Serialize task model for detail view API responses"""
    return TaskDetailSchema(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_by=serialize_user_minimal(task.created_by),
        assigned_to=[serialize_user_minimal(user) for user in task.assigned_to.all()],
        tags=[serialize_tag(tag) for tag in task.tags.all()],
        team=serialize_team(task.team) if task.team else None,
        parent_task_id=task.parent_task.id if task.parent_task else None,
        metadata=task.metadata,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_archived=task.is_archived,
        is_overdue=task.is_past_due
    )


def serialize_history(history_item):
    """Serialize task history item to API schema"""
    return TaskHistorySchema(
        id=history_item.id,
        action=history_item.action,
        changes=history_item.changes,
        timestamp=history_item.timestamp,
        user=serialize_user_minimal(history_item.user)
    )