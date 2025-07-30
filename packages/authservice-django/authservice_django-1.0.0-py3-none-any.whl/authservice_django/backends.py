from typing import Optional, Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

from .client import AuthServiceClient
from .config import get_config
from .exceptions import TokenError, AuthServiceError


User = get_user_model()


class AuthServiceBackend(BaseBackend):
    """
    Django authentication backend for Auth Service.
    
    This backend authenticates users via Auth Service tokens and optionally
    creates/updates local user records.
    """
    
    def __init__(self):
        self.config = get_config()
        self.client = AuthServiceClient(self.config)
    
    def authenticate(
        self,
        request: Optional[HttpRequest] = None,
        token: Optional[str] = None,
        **kwargs
    ) -> Optional[AbstractBaseUser]:
        """
        Authenticate user with Auth Service token.
        
        Args:
            request: The Django request object
            token: The Auth Service JWT token
            **kwargs: Additional arguments (ignored)
        
        Returns:
            User instance if authentication successful, None otherwise
        """
        if not token:
            return None
        
        try:
            # Verify token and get user info
            user_data = self.client.verify_token(token)
            
            # Get or create user
            user = self._get_or_create_user(user_data, token)
            
            # Store token on user for later use
            if user and hasattr(user, "_auth_service_token"):
                user._auth_service_token = token
            
            return user
            
        except TokenError:
            # Invalid token
            return None
        except AuthServiceError:
            # Auth service error - fail authentication
            return None
        except Exception as e:
            # Log unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in AuthServiceBackend: {e}")
            return None
    
    def get_user(self, user_id: Any) -> Optional[AbstractBaseUser]:
        """
        Get user by ID.
        
        Args:
            user_id: The user's primary key
        
        Returns:
            User instance if found, None otherwise
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def _get_or_create_user(
        self, user_data: dict, token: str
    ) -> Optional[AbstractBaseUser]:
        """
        Get or create local user from Auth Service data.
        
        Args:
            user_data: User data from Auth Service
            token: The auth token
        
        Returns:
            User instance
        """
        # Extract user info
        user_id = user_data.get("id") or user_data.get("userId")
        email = user_data.get("email")
        
        if not user_id:
            return None
        
        # Build lookup kwargs
        lookup_kwargs = {}
        defaults = {}
        
        # Use email as username if User model has username field
        if hasattr(User, "username"):
            if email:
                lookup_kwargs["username"] = email.split("@")[0]  # Use email prefix
                defaults["email"] = email
            else:
                lookup_kwargs["username"] = f"user_{user_id}"
        elif hasattr(User, "email"):
            if email:
                lookup_kwargs["email"] = email
            else:
                # Can't create user without email if it's the primary identifier
                return None
        
        # Set auth service user ID
        if hasattr(User, "auth_service_id"):
            lookup_kwargs["auth_service_id"] = user_id
        elif hasattr(User, "external_id"):
            lookup_kwargs["external_id"] = user_id
        
        # Create or update user
        if self.config.create_users:
            user, created = User.objects.get_or_create(
                **lookup_kwargs,
                defaults=defaults
            )
            
            # Update user if configured
            if not created and self.config.update_users:
                updated = False
                
                if email and hasattr(user, "email") and user.email != email:
                    user.email = email
                    updated = True
                
                # Update additional fields if they exist
                if hasattr(user, "first_name") and user_data.get("firstName"):
                    user.first_name = user_data["firstName"]
                    updated = True
                
                if hasattr(user, "last_name") and user_data.get("lastName"):
                    user.last_name = user_data["lastName"]
                    updated = True
                
                if updated:
                    user.save()
            
            # Sync permissions if configured
            if self.config.sync_permissions and hasattr(user, "user_permissions"):
                self._sync_permissions(user, token)
            
            return user
        else:
            # Just try to get existing user
            try:
                return User.objects.get(**lookup_kwargs)
            except User.DoesNotExist:
                return None
    
    def _sync_permissions(self, user: AbstractBaseUser, token: str) -> None:
        """
        Sync user permissions from Auth Service.
        
        Args:
            user: The Django user instance
            token: The auth token
        """
        try:
            # Get permissions from Auth Service
            perm_data = self.client.get_user_permissions(token)
            permissions = perm_data.get("permissions", [])
            
            # Convert to Django permission format
            django_perms = []
            for perm in permissions:
                resource = perm.get("resource", "")
                action = perm.get("action", "")
                
                # Map to Django permission format (app_label.codename)
                # You might want to customize this mapping
                if resource and action:
                    # Example: posts:create -> blog.add_post
                    app_label = resource.lower()
                    if action == "create":
                        codename = f"add_{resource.lower()}"
                    elif action == "read":
                        codename = f"view_{resource.lower()}"
                    elif action == "update":
                        codename = f"change_{resource.lower()}"
                    elif action == "delete":
                        codename = f"delete_{resource.lower()}"
                    else:
                        codename = f"{action}_{resource.lower()}"
                    
                    django_perms.append(f"{app_label}.{codename}")
            
            # Update user permissions
            if django_perms and hasattr(user, "user_permissions"):
                from django.contrib.auth.models import Permission
                
                # Get Permission objects
                permissions = Permission.objects.filter(
                    content_type__app_label__in=[p.split(".")[0] for p in django_perms],
                    codename__in=[p.split(".")[1] for p in django_perms]
                )
                
                # Set permissions
                user.user_permissions.set(permissions)
        
        except Exception as e:
            # Log but don't fail authentication
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to sync permissions: {e}")
    
    def has_perm(
        self, user_obj: AbstractBaseUser, perm: str, obj: Any = None
    ) -> bool:
        """
        Check if user has permission.
        
        This method checks permissions with Auth Service if the user has a token,
        otherwise falls back to Django's default permission system.
        
        Args:
            user_obj: The user to check permissions for
            perm: The permission string (e.g., 'app_label.permission')
            obj: Optional object (not used)
        
        Returns:
            True if user has permission, False otherwise
        """
        if not user_obj or not user_obj.is_active:
            return False
        
        # Check if user is superuser
        if user_obj.is_superuser:
            return True
        
        # Check if user has auth service token
        token = getattr(user_obj, "_auth_service_token", None)
        if token:
            # Convert Django permission format to Auth Service format
            # e.g., blog.add_post -> posts:create
            if "." in perm:
                app_label, codename = perm.split(".", 1)
                
                # Map Django permission to Auth Service format
                # You might want to customize this mapping
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
                    # Custom permission
                    parts = codename.split("_", 1)
                    if len(parts) == 2:
                        action, resource = parts
                    else:
                        resource = app_label
                        action = codename
                
                auth_service_perm = f"{resource}:{action}"
                
                # Check with Auth Service
                try:
                    return self.client.check_permission(token, auth_service_perm)
                except:
                    # Fall back to Django permissions
                    pass
        
        # Fall back to Django's permission system
        return user_obj.has_perm(perm)