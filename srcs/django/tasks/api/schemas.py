"""
Task Management API Schemas
Data validation and serialization schemas for task operations
"""

from ninja import Schema
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class TaskBaseSchema(Schema):
    """Base schema for task data"""
    title: str
    description: str
    status: str = "todo"
    priority: str = "medium"
    due_date: datetime
    estimated_hours: Optional[Decimal] = None


class TaskCreateSchema(TaskBaseSchema):
    """Schema for creating a new task"""
    assigned_to_ids: Optional[List[int]] = []
    tag_ids: Optional[List[int]] = []
    parent_task_id: Optional[int] = None
    team_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}


class TaskUpdateSchema(Schema):
    """Schema for updating an existing task"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    assigned_to_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskPatchSchema(Schema):
    """Schema for partial updates (PATCH)"""
    status: Optional[str] = None
    priority: Optional[str] = None
    actual_hours: Optional[Decimal] = None


class UserMinimalSchema(Schema):
    """Minimal user info for task responses"""
    id: int
    username: str
    email: str


class TagSchema(Schema):
    """Tag schema for task responses"""
    id: int
    name: str
    color: str


class TeamSchema(Schema):
    """Team schema for task responses"""
    id: int
    name: str


class TaskDetailSchema(Schema):
    """Complete task information for detail view"""
    id: int
    title: str
    description: str
    status: str
    priority: str
    due_date: datetime
    estimated_hours: Decimal
    actual_hours: Optional[Decimal]
    created_by: UserMinimalSchema
    assigned_to: List[UserMinimalSchema]
    tags: List[TagSchema]
    team: Optional[TeamSchema]
    parent_task_id: Optional[int]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    is_overdue: bool


class TaskListSchema(Schema):
    """Simplified task information for list view"""
    id: int
    title: str
    status: str
    priority: str
    due_date: datetime
    estimated_hours: Decimal
    created_by: UserMinimalSchema
    assigned_to: List[UserMinimalSchema]
    tags: List[TagSchema]
    created_at: datetime
    is_overdue: bool


class PaginatedTasksSchema(Schema):
    """Paginated task list response"""
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[TaskListSchema]


class TaskDeleteResponseSchema(Schema):
    """Response for task deletion"""
    success: bool
    message: str


class TaskErrorSchema(Schema):
    """Error response schema"""
    error: str
    details: Optional[Dict[str, Any]] = None
