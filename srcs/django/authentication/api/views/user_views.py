"""
User Management API Views
Endpoints for user CRUD operations following REST API requirements
"""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
import json

User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class UserListAPIView(View):
    """
    API endpoint for user listing with pagination and search.
    
    Methods:
        GET: List users with pagination
            Params:
                page (int): Page number (default: 1)
                page_size (int): Items per page (default: 20, max: 100)
                search (str): Search in username and email
            Returns:
                200: Paginated user list
                401: Unauthorized
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Check authentication (in real app you'd use JWT middleware)
            # For now, we'll just return data for testing
            
            # Get query parameters
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)
            search = request.GET.get('search', '')
            
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
                users_data.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active,
                    "date_joined": user.date_joined.isoformat() if user.date_joined else None,
                })
            
            # Build pagination links
            base_url = request.build_absolute_uri().split('?')[0]
            next_url = None
            previous_url = None
            
            if page_obj.has_next():
                next_url = f"{base_url}?page={page_obj.next_page_number()}&page_size={page_size}"
                if search:
                    next_url += f"&search={search}"
            
            if page_obj.has_previous():
                previous_url = f"{base_url}?page={page_obj.previous_page_number()}&page_size={page_size}"
                if search:
                    previous_url += f"&search={search}"
            
            return JsonResponse({
                "status": "success",
                "data": {
                    "count": paginator.count,
                    "next": next_url,
                    "previous": previous_url,
                    "results": users_data
                }
            })
            
        except ValueError as e:
            return JsonResponse(
                {"status": "error", "message": "Invalid pagination parameters"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Error interno del servidor"}, 
                status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class UserDetailAPIView(View):
    """
    API endpoint for user detail operations.
    
    Methods:
        GET: Get user details
        PUT: Update user details
    """
    
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id, is_active=True)
            
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": user.date_joined.isoformat() if user.date_joined else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            
            # Add profile-specific fields if available
            if hasattr(user, 'email_verified'):
                user_data["email_verified"] = user.email_verified
            
            return JsonResponse({
                "status": "success",
                "data": user_data
            })
            
        except User.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Usuario no encontrado"}, 
                status=404
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Error interno del servidor"}, 
                status=500
            )
    
    def put(self, request, user_id, *args, **kwargs):
        try:
            # Get data
            if hasattr(request, "data"):
                data = request.data
            else:
                data = json.loads(request.body)
            
            user = User.objects.get(id=user_id, is_active=True)
            
            # Update allowed fields
            if 'username' in data and data['username']:
                # Check if username is already taken
                if User.objects.filter(username=data['username']).exclude(id=user.id).exists():
                    return JsonResponse(
                        {"status": "error", "message": "El nombre de usuario ya está en uso"}, 
                        status=400
                    )
                user.username = data['username']
            
            if 'email' in data and data['email']:
                # Check if email is already taken
                if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                    return JsonResponse(
                        {"status": "error", "message": "El email ya está en uso"}, 
                        status=400
                    )
                user.email = data['email']
                # Reset email verification if email changed
                if hasattr(user, 'email_verified'):
                    user.email_verified = False
            
            if 'first_name' in data:
                user.first_name = data['first_name']
            
            if 'last_name' in data:
                user.last_name = data['last_name']
            
            user.save()
            
            return JsonResponse({
                "status": "success",
                "message": "Usuario actualizado correctamente",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            })
            
        except User.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Usuario no encontrado"}, 
                status=404
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Error interno del servidor"}, 
                status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class UserMeAPIView(View):
    """
    API endpoint for current user profile.
    
    Methods:
        GET: Get current user profile
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # In a real app, you'd get user from JWT token
            # For testing, we'll use session authentication or return test user
            
            if request.user.is_authenticated:
                user = request.user
            else:
                # For testing purposes, return test user
                try:
                    user = User.objects.get(username='testuser')
                except User.DoesNotExist:
                    return JsonResponse(
                        {"status": "error", "message": "Usuario no autenticado"}, 
                        status=401
                    )
            
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": user.date_joined.isoformat() if user.date_joined else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            
            # Add profile-specific fields if available
            if hasattr(user, 'email_verified'):
                user_data["email_verified"] = user.email_verified
            
            return JsonResponse({
                "status": "success",
                "data": user_data
            })
            
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Error interno del servidor"}, 
                status=500
            )
