from typing import List, Optional
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from ..client import AuthServiceClient


class BaseAuthServicePermission(permissions.BasePermission):
    """Base permission class for Auth Service integration"""
    
    def __init__(self):
        self.client = AuthServiceClient()
    
    def get_auth_token(self, request: Request) -> Optional[str]:
        """Get auth token from request or user"""
        # Try request auth (from authentication)
        if hasattr(request, "auth") and isinstance(request.auth, str):
            return request.auth
        
        # Try user token
        if hasattr(request.user, "_auth_service_token"):
            return request.user._auth_service_token
        
        return None


class IsAuthenticated(BaseAuthServicePermission):
    """
    Permission class that requires authentication.
    
    This is similar to DRF's IsAuthenticated but ensures
    the user has a valid Auth Service token.
    """
    
    message = "Authentication required"
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is authenticated with valid token"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verify token exists
        token = self.get_auth_token(request)
        return bool(token)


class HasPermission(BaseAuthServicePermission):
    """
    Permission class that checks for a specific permission.
    
    Usage:
        class PostViewSet(viewsets.ModelViewSet):
            permission_classes = [HasPermission]
            required_permission = "posts:create"
            
            # Or use get_required_permission() for dynamic permissions
            def get_required_permission(self):
                if self.action == "create":
                    return "posts:create"
                elif self.action == "update":
                    return "posts:edit"
                return None
    """
    
    message = "You do not have permission to perform this action"
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user has required permission"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required permission
        permission = self.get_required_permission(view, request)
        if not permission:
            return True  # No permission required
        
        # Get token
        token = self.get_auth_token(request)
        if not token:
            return False
        
        # Check permission
        try:
            return self.client.check_permission(token, permission)
        except:
            return False
    
    def get_required_permission(self, view: APIView, request: Request) -> Optional[str]:
        """Get required permission from view"""
        # Check for method-specific permission
        method_permission = getattr(
            view, f"{request.method.lower()}_permission", None
        )
        if method_permission:
            return method_permission
        
        # Check for action-specific permission (ViewSet)
        if hasattr(view, "action") and view.action:
            action_permission = getattr(
                view, f"{view.action}_permission", None
            )
            if action_permission:
                return action_permission
        
        # Check for general required permission
        if hasattr(view, "get_required_permission"):
            return view.get_required_permission()
        
        return getattr(view, "required_permission", None)


class HasAnyPermission(BaseAuthServicePermission):
    """
    Permission class that checks if user has any of the required permissions.
    
    Usage:
        class PostViewSet(viewsets.ModelViewSet):
            permission_classes = [HasAnyPermission]
            required_permissions = ["posts:edit", "posts:admin"]
    """
    
    message = "You do not have any of the required permissions"
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user has any of the required permissions"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required permissions
        permissions = self.get_required_permissions(view, request)
        if not permissions:
            return True  # No permissions required
        
        # Get token
        token = self.get_auth_token(request)
        if not token:
            return False
        
        # Check permissions
        try:
            return self.client.has_any_permission(token, permissions)
        except:
            return False
    
    def get_required_permissions(self, view: APIView, request: Request) -> List[str]:
        """Get required permissions from view"""
        if hasattr(view, "get_required_permissions"):
            return view.get_required_permissions()
        
        return getattr(view, "required_permissions", [])


class HasAllPermissions(BaseAuthServicePermission):
    """
    Permission class that checks if user has all required permissions.
    
    Usage:
        class AdminViewSet(viewsets.ModelViewSet):
            permission_classes = [HasAllPermissions]
            required_permissions = ["admin:access", "posts:manage"]
    """
    
    message = "You do not have all required permissions"
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user has all required permissions"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required permissions
        permissions = self.get_required_permissions(view, request)
        if not permissions:
            return True  # No permissions required
        
        # Get token
        token = self.get_auth_token(request)
        if not token:
            return False
        
        # Check permissions
        try:
            return self.client.has_all_permissions(token, permissions)
        except:
            return False
    
    def get_required_permissions(self, view: APIView, request: Request) -> List[str]:
        """Get required permissions from view"""
        if hasattr(view, "get_required_permissions"):
            return view.get_required_permissions()
        
        return getattr(view, "required_permissions", [])


class DjangoModelPermissions(HasPermission):
    """
    Permission class that maps Django model permissions to Auth Service.
    
    This is compatible with DRF's DjangoModelPermissions but uses
    Auth Service for permission checks.
    
    Usage:
        class PostViewSet(viewsets.ModelViewSet):
            permission_classes = [DjangoModelPermissions]
            queryset = Post.objects.all()
    """
    
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
    
    def get_required_permission(self, view: APIView, request: Request) -> Optional[str]:
        """Get required permission based on model and action"""
        # Get model
        model_cls = getattr(view, "queryset", None)
        if model_cls is not None:
            model_cls = model_cls.model
        else:
            model_cls = getattr(view, "model", None)
        
        if not model_cls:
            return None
        
        # Get permission format
        perms = self.perms_map.get(request.method, [])
        if not perms:
            return None
        
        # Format permission
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        
        # Return first permission (simplified)
        if perms:
            django_perm = perms[0] % kwargs
            
            # Convert to Auth Service format
            # e.g., blog.add_post -> posts:create
            app_label, codename = django_perm.split(".", 1)
            
            if codename.startswith("add_"):
                resource = codename[4:]
                action = "create"
            elif codename.startswith("change_"):
                resource = codename[7:]
                action = "update"
            elif codename.startswith("delete_"):
                resource = codename[7:]
                action = "delete"
            elif codename.startswith("view_"):
                resource = codename[5:]
                action = "read"
            else:
                resource = model_cls._meta.model_name
                action = codename
            
            return f"{resource}:{action}"
        
        return None


class IsOwner(BaseAuthServicePermission):
    """
    Permission class that checks if user owns the object.
    
    Usage:
        class PostViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsOwner]
            owner_field = "author"  # Field that references the owner
    """
    
    message = "You do not own this object"
    
    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        """Check if user owns the object"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get owner field
        owner_field = getattr(view, "owner_field", "user")
        
        # Get owner
        owner = getattr(obj, owner_field, None)
        
        # Check if user is owner
        return owner == request.user


class HasRole(BaseAuthServicePermission):
    """
    Permission class that checks if user has specific role.
    
    Usage:
        class ModeratorViewSet(viewsets.ModelViewSet):
            permission_classes = [HasRole]
            required_role = "moderator"
            # or
            required_roles = ["moderator", "admin"]  # Any of these
    """
    
    message = "You do not have the required role"
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user has required role"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get user roles
        if not hasattr(request, "auth_roles"):
            return False
        
        user_roles = set(r.get("name", "") for r in request.auth_roles)
        
        # Get required roles
        required_roles = self.get_required_roles(view)
        if not required_roles:
            return True
        
        # Check if user has any required role
        return bool(set(required_roles).intersection(user_roles))
    
    def get_required_roles(self, view: APIView) -> List[str]:
        """Get required roles from view"""
        # Single role
        role = getattr(view, "required_role", None)
        if role:
            return [role]
        
        # Multiple roles
        return getattr(view, "required_roles", [])