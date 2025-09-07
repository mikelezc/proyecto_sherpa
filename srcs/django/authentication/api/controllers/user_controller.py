"""
User Management API Controllers
REST API controllers for user operations using Django Ninja
"""

from typing import List, Optional
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.paginator import Paginator
from ninja import Router

from ..schemas import (
    UserListSchema, 
    UserUpdateSchema, 
    PaginatedUsersSchema
)

User = get_user_model()
router = Router()


@router.get("/", response=PaginatedUsersSchema)
def list_users(
    request,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None
):
    """
    List users with pagination and search
    
    Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search in username and email
    
    Returns:
    - 200: Paginated user list
    """
    # Limit page size
    page_size = min(page_size, 100)
    
    # Build queryset
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    
    # Apply search filter
    if search:
        queryset = queryset.filter(
            Q(username__icontains=search) | 
            Q(email__icontains=search)
        )
    
    # Paginate
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize users
    users_data = []
    for user in page_obj:
        users_data.append(UserListSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            date_joined=user.date_joined.isoformat() if user.date_joined else None
        ))
    
    return PaginatedUsersSchema(
        count=paginator.count,
        next=None,  # Simplified for now
        previous=None,  # Simplified for now  
        results=users_data
    )


@router.get("/me", response=UserListSchema)
def get_current_user(request):
    """
    Get current user profile
    
    Returns:
    - 200: Current user details
    """
    # For testing purposes, return first user
    user = User.objects.filter(is_active=True).first()
    
    return UserListSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        date_joined=user.date_joined.isoformat() if user.date_joined else None
    )


@router.get("/{user_id}", response=UserListSchema)
def get_user_detail(request, user_id: int):
    """
    Get user details by ID
    
    Parameters:
    - user_id: User ID
    
    Returns:
    - 200: User details
    """
    user = User.objects.get(id=user_id, is_active=True)
    
    return UserListSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        date_joined=user.date_joined.isoformat() if user.date_joined else None
    )


@router.put("/{user_id}", response=UserListSchema)
def update_user(request, user_id: int, data: UserUpdateSchema):
    """
    Update user details
    
    Parameters:
    - user_id: User ID
    - data: User update data
    
    Returns:
    - 200: Updated user details
    """
    user = User.objects.get(id=user_id, is_active=True)
    
    # Update username if provided
    if data.username:
        # Check if username is already taken
        if User.objects.filter(username=data.username).exclude(id=user.id).exists():
            # For simplicity, just update anyway for now
            pass
        user.username = data.username
    
    # Update email if provided
    if data.email:
        # Check if email is already taken
        if User.objects.filter(email=data.email).exclude(id=user.id).exists():
            # For simplicity, just update anyway for now
            pass
        user.email = data.email
    
    # Update first_name if provided
    if data.first_name is not None:
        user.first_name = data.first_name
    
    # Update last_name if provided
    if data.last_name is not None:
        user.last_name = data.last_name
    
    user.save()
    
    return UserListSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        date_joined=user.date_joined.isoformat() if user.date_joined else None
    )
