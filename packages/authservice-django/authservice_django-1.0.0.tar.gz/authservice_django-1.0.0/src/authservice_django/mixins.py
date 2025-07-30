from typing import List, Optional, Any
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from .client import AuthServiceClient
from .config import get_config


class AuthServiceMixin:
    """Base mixin for Auth Service integration"""
    
    def get_auth_token(self) -> Optional[str]:
        """Get auth token from request"""
        if hasattr(self.request, "auth_token"):
            return self.request.auth_token
        
        if hasattr(self.request.user, "_auth_service_token"):
            return self.request.user._auth_service_token
        
        # Try to extract from request
        auth_header = self.request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        return None
    
    def check_auth_permission(self, permission: str) -> bool:
        """Check permission using Auth Service"""
        token = self.get_auth_token()
        if not token:
            return False
        
        client = AuthServiceClient()
        return client.check_permission(token, permission)
    
    def check_auth_permissions(
        self, permissions: List[str], require_all: bool = False
    ) -> bool:
        """Check multiple permissions using Auth Service"""
        token = self.get_auth_token()
        if not token:
            return False
        
        client = AuthServiceClient()
        if require_all:
            return client.has_all_permissions(token, permissions)
        else:
            return client.has_any_permission(token, permissions)


class LoginRequiredMixin(AuthServiceMixin, AccessMixin):
    """
    Mixin to require authentication for class-based views.
    
    Usage:
        class MyView(LoginRequiredMixin, View):
            ...
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(AuthServiceMixin, AccessMixin):
    """
    Mixin to require specific permissions for class-based views.
    
    Usage:
        class CreatePostView(PermissionRequiredMixin, CreateView):
            permission_required = "posts:create"
            # or
            permission_required = ["posts:create", "posts:publish"]
    """
    
    permission_required: Optional[Any] = None
    
    def get_permission_required(self) -> List[str]:
        """
        Get the required permissions.
        
        Returns:
            List of permission strings
        """
        if self.permission_required is None:
            raise ValueError(
                f"{self.__class__.__name__} is missing the "
                "permission_required attribute."
            )
        
        if isinstance(self.permission_required, str):
            perms = [self.permission_required]
        else:
            perms = list(self.permission_required)
        
        return perms
    
    def has_permission(self) -> bool:
        """
        Check if the user has the required permissions.
        
        Returns:
            True if user has permission, False otherwise
        """
        perms = self.get_permission_required()
        
        # Try Auth Service first
        token = self.get_auth_token()
        if token:
            return self.check_auth_permissions(perms, require_all=True)
        
        # Fall back to Django permissions
        return self.request.user.has_perms(perms)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not self.has_permission():
            return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self):
        """Handle permission denied"""
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        
        # Return JSON for API requests
        if self.request.path.startswith(("/api/", "/rest/")):
            return JsonResponse(
                {
                    "error": "Permission denied",
                    "required": self.get_permission_required()
                },
                status=403
            )
        
        return super().handle_no_permission()


class MultiplePermissionsRequiredMixin(PermissionRequiredMixin):
    """
    Mixin to require multiple permissions with AND/OR logic.
    
    Usage:
        class AdminView(MultiplePermissionsRequiredMixin, View):
            permissions = {
                "all": ["admin:access"],  # Required
                "any": ["posts:edit", "posts:admin"]  # At least one
            }
    """
    
    permissions: Optional[dict] = None
    
    def get_permissions(self) -> dict:
        """Get permissions configuration"""
        if self.permissions is None:
            raise ValueError(
                f"{self.__class__.__name__} is missing the "
                "permissions attribute."
            )
        return self.permissions
    
    def has_permission(self) -> bool:
        """Check if user has required permissions"""
        perms = self.get_permissions()
        
        # Check "all" permissions (AND)
        all_perms = perms.get("all", [])
        if all_perms:
            token = self.get_auth_token()
            if token:
                if not self.check_auth_permissions(all_perms, require_all=True):
                    return False
            else:
                if not self.request.user.has_perms(all_perms):
                    return False
        
        # Check "any" permissions (OR)
        any_perms = perms.get("any", [])
        if any_perms:
            token = self.get_auth_token()
            if token:
                if not self.check_auth_permissions(any_perms, require_all=False):
                    return False
            else:
                if not any(self.request.user.has_perm(p) for p in any_perms):
                    return False
        
        return True
    
    def get_permission_required(self) -> List[str]:
        """Get all required permissions for error messages"""
        perms = self.get_permissions()
        all_perms = perms.get("all", [])
        any_perms = perms.get("any", [])
        return all_perms + any_perms


class OwnerRequiredMixin(AuthServiceMixin):
    """
    Mixin to require that the user owns the object.
    
    Usage:
        class EditPostView(OwnerRequiredMixin, UpdateView):
            model = Post
            owner_field = "author"  # Field that references the owner
            # or override get_owner()
    """
    
    owner_field: str = "user"
    allow_staff: bool = True
    
    def get_owner(self, obj: Any) -> Any:
        """Get the owner of the object"""
        return getattr(obj, self.owner_field, None)
    
    def is_owner(self, obj: Any) -> bool:
        """Check if current user owns the object"""
        if not self.request.user.is_authenticated:
            return False
        
        # Staff can access if allowed
        if self.allow_staff and self.request.user.is_staff:
            return True
        
        owner = self.get_owner(obj)
        return owner == self.request.user
    
    def get_object(self, queryset=None):
        """Get object and check ownership"""
        obj = super().get_object(queryset)
        
        if not self.is_owner(obj):
            raise PermissionDenied("You don't have permission to access this object")
        
        return obj


class RoleRequiredMixin(AuthServiceMixin, AccessMixin):
    """
    Mixin to require specific roles for class-based views.
    
    Usage:
        class ModeratorView(RoleRequiredMixin, View):
            required_roles = ["moderator", "admin"]
            require_all_roles = False  # User needs at least one role
    """
    
    required_roles: Optional[List[str]] = None
    require_all_roles: bool = False
    
    def get_required_roles(self) -> List[str]:
        """Get required roles"""
        if self.required_roles is None:
            raise ValueError(
                f"{self.__class__.__name__} is missing the "
                "required_roles attribute."
            )
        return self.required_roles
    
    def has_required_roles(self) -> bool:
        """Check if user has required roles"""
        if not hasattr(self.request, "user_roles"):
            return False
        
        required = set(self.get_required_roles())
        user_roles = set(r.get("name", "") for r in self.request.user_roles)
        
        if self.require_all_roles:
            return required.issubset(user_roles)
        else:
            return bool(required.intersection(user_roles))
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not self.has_required_roles():
            return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)