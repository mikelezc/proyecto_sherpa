"""
User Management API Controllers
REST API controllers for user operations using Django Ninja
ALL ENDPOINTS REQUIRE AUTHENTICATION
"""

from typing import Optional
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.paginator import Paginator
from ninja import Router
from ninja.errors import HttpError

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
    REQUIRES: Administrator permissions
    
    Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search in username and email
    
    Returns:
    - 200: Paginated user list
    - 403: Forbidden (non-admin users)
    """
    # CRITICAL VALIDATION: Only administrators can list users
    if not request.user.is_staff:
        raise HttpError(403, "Administrator permissions required")
    
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
    REQUIRES: Authenticated user
    
    Returns:
    - 200: Current user details
    """
    # CRITICAL FIX: Use authenticated user, NOT first user
    user = request.user
    
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
    REQUIRES: User can only view own profile, admin can view any
    
    Parameters:
    - user_id: User ID
    
    Returns:
    - 200: User details
    - 403: Forbidden (access denied)
    - 404: User not found
    """
    # CRITICAL VALIDATION: User can only view own profile or admin can view all
    if request.user.id != user_id and not request.user.is_staff:
        raise HttpError(403, "Access denied. You can only view your own profile.")
    
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")
    
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
    REQUIRES: User can only edit own profile, admin can edit any
    
    Parameters:
    - user_id: User ID
    - data: User update data
    
    Returns:
    - 200: Updated user details
    - 400: Bad request (validation errors)
    - 403: Forbidden (access denied)
    - 404: User not found
    """
    # CRITICAL VALIDATION: User can only edit own profile or admin can edit all
    if request.user.id != user_id and not request.user.is_staff:
        raise HttpError(403, "Access denied. You can only edit your own profile.")
    
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")
    
    # Update username if provided
    if data.username:
        # Check if username is already taken
        if User.objects.filter(username=data.username).exclude(id=user.id).exists():
            raise HttpError(400, "Username already taken")
        user.username = data.username
    
    # Update email if provided
    if data.email:
        # Check if email is already taken
        if User.objects.filter(email=data.email).exclude(id=user.id).exists():
            raise HttpError(400, "EEmail already in use")
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
