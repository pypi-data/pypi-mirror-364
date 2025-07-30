from functools import wraps
from typing import List, Optional, Callable, Union
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from .client import AuthServiceClient
from .config import get_config


def require_auth(
    function: Optional[Callable] = None,
    redirect_url: Optional[str] = None,
    raise_exception: bool = False
) -> Callable:
    """
    Decorator to require authentication for a view.
    
    Args:
        function: The view function to decorate
        redirect_url: URL to redirect to if not authenticated (default: LOGIN_URL)
        raise_exception: Whether to raise PermissionDenied instead of redirecting
    
    Usage:
        @require_auth
        def my_view(request):
            ...
        
        @require_auth(redirect_url='/custom-login/')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated:
                if raise_exception:
                    raise PermissionDenied("Authentication required")
                
                # Check if it's an API request
                if request.path.startswith(("/api/", "/rest/")):
                    return JsonResponse(
                        {"error": "Authentication required"},
                        status=401
                    )
                
                # Redirect to login
                config = get_config()
                login_url = redirect_url or config.login_url
                return redirect(f"{login_url}?next={request.path}")
            
            return view_func(request, *args, **kwargs)
        
        # Mark view as requiring auth (for middleware)
        wrapped_view._auth_required = True
        return wrapped_view
    
    if function:
        return decorator(function)
    return decorator


def require_permission(
    permission: str,
    redirect_url: Optional[str] = None,
    raise_exception: bool = False
) -> Callable:
    """
    Decorator to require a specific permission for a view.
    
    Args:
        permission: The required permission (e.g., "posts:create")
        redirect_url: URL to redirect to if permission denied
        raise_exception: Whether to raise PermissionDenied instead of redirecting
    
    Usage:
        @require_permission("posts:create")
        def create_post(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated:
                if raise_exception:
                    raise PermissionDenied("Authentication required")
                
                config = get_config()
                return redirect(f"{config.login_url}?next={request.path}")
            
            # Check permission
            token = getattr(request.user, "_auth_service_token", None) or \
                    getattr(request, "auth_token", None)
            
            if token:
                client = AuthServiceClient()
                has_permission = client.check_permission(token, permission)
            else:
                # Fall back to Django permissions
                has_permission = request.user.has_perm(permission)
            
            if not has_permission:
                if raise_exception:
                    raise PermissionDenied(f"Permission required: {permission}")
                
                # Check if it's an API request
                if request.path.startswith(("/api/", "/rest/")):
                    return JsonResponse(
                        {
                            "error": "Permission denied",
                            "required": permission
                        },
                        status=403
                    )
                
                # Redirect to unauthorized page
                config = get_config()
                unauthorized_url = redirect_url or config.unauthorized_redirect_url
                return redirect(unauthorized_url)
            
            return view_func(request, *args, **kwargs)
        
        # Mark view with required permissions (for middleware)
        wrapped_view._auth_required = True
        wrapped_view._required_permissions = [permission]
        return wrapped_view
    
    return decorator


def require_any_permission(
    permissions: List[str],
    redirect_url: Optional[str] = None,
    raise_exception: bool = False
) -> Callable:
    """
    Decorator to require any of the specified permissions for a view.
    
    Args:
        permissions: List of permissions (user needs at least one)
        redirect_url: URL to redirect to if permission denied
        raise_exception: Whether to raise PermissionDenied instead of redirecting
    
    Usage:
        @require_any_permission(["posts:edit", "posts:admin"])
        def edit_post(request, post_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated:
                if raise_exception:
                    raise PermissionDenied("Authentication required")
                
                config = get_config()
                return redirect(f"{config.login_url}?next={request.path}")
            
            # Check permissions
            token = getattr(request.user, "_auth_service_token", None) or \
                    getattr(request, "auth_token", None)
            
            if token:
                client = AuthServiceClient()
                has_permission = client.has_any_permission(token, permissions)
            else:
                # Fall back to Django permissions
                has_permission = any(
                    request.user.has_perm(perm) for perm in permissions
                )
            
            if not has_permission:
                if raise_exception:
                    raise PermissionDenied(
                        f"One of these permissions required: {', '.join(permissions)}"
                    )
                
                # Check if it's an API request
                if request.path.startswith(("/api/", "/rest/")):
                    return JsonResponse(
                        {
                            "error": "Permission denied",
                            "required": permissions,
                            "require_any": True
                        },
                        status=403
                    )
                
                # Redirect to unauthorized page
                config = get_config()
                unauthorized_url = redirect_url or config.unauthorized_redirect_url
                return redirect(unauthorized_url)
            
            return view_func(request, *args, **kwargs)
        
        # Mark view with required permissions (for middleware)
        wrapped_view._auth_required = True
        wrapped_view._required_permissions = permissions
        wrapped_view._require_all_permissions = False
        return wrapped_view
    
    return decorator


def require_all_permissions(
    permissions: List[str],
    redirect_url: Optional[str] = None,
    raise_exception: bool = False
) -> Callable:
    """
    Decorator to require all of the specified permissions for a view.
    
    Args:
        permissions: List of permissions (user needs all)
        redirect_url: URL to redirect to if permission denied
        raise_exception: Whether to raise PermissionDenied instead of redirecting
    
    Usage:
        @require_all_permissions(["admin:access", "posts:delete"])
        def delete_all_posts(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated:
                if raise_exception:
                    raise PermissionDenied("Authentication required")
                
                config = get_config()
                return redirect(f"{config.login_url}?next={request.path}")
            
            # Check permissions
            token = getattr(request.user, "_auth_service_token", None) or \
                    getattr(request, "auth_token", None)
            
            if token:
                client = AuthServiceClient()
                has_permission = client.has_all_permissions(token, permissions)
            else:
                # Fall back to Django permissions
                has_permission = all(
                    request.user.has_perm(perm) for perm in permissions
                )
            
            if not has_permission:
                if raise_exception:
                    raise PermissionDenied(
                        f"All of these permissions required: {', '.join(permissions)}"
                    )
                
                # Check if it's an API request
                if request.path.startswith(("/api/", "/rest/")):
                    return JsonResponse(
                        {
                            "error": "Permission denied",
                            "required": permissions,
                            "require_all": True
                        },
                        status=403
                    )
                
                # Redirect to unauthorized page
                config = get_config()
                unauthorized_url = redirect_url or config.unauthorized_redirect_url
                return redirect(unauthorized_url)
            
            return view_func(request, *args, **kwargs)
        
        # Mark view with required permissions (for middleware)
        wrapped_view._auth_required = True
        wrapped_view._required_permissions = permissions
        wrapped_view._require_all_permissions = True
        return wrapped_view
    
    return decorator


def permission_required(
    perm: Union[str, List[str]],
    login_url: Optional[str] = None,
    raise_exception: bool = False
) -> Callable:
    """
    Django-compatible permission_required decorator.
    
    This is a compatibility wrapper that works like Django's built-in
    permission_required but uses Auth Service for permission checks.
    
    Args:
        perm: Permission string or list of permissions
        login_url: URL to redirect to if not authenticated
        raise_exception: Whether to raise PermissionDenied
    
    Usage:
        @permission_required("blog.add_post")
        def create_post(request):
            ...
    """
    if isinstance(perm, str):
        return require_permission(perm, redirect_url=login_url, raise_exception=raise_exception)
    else:
        return require_all_permissions(perm, redirect_url=login_url, raise_exception=raise_exception)


# Async decorators for Django 4.1+
def require_auth_async(
    function: Optional[Callable] = None,
    raise_exception: bool = True
) -> Callable:
    """
    Async decorator to require authentication.
    
    Usage:
        @require_auth_async
        async def my_async_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapped_view(request: HttpRequest, *args, **kwargs):
            if not hasattr(request, "auth_user") or not request.auth_user:
                if raise_exception:
                    raise PermissionDenied("Authentication required")
                
                return JsonResponse(
                    {"error": "Authentication required"},
                    status=401
                )
            
            return await view_func(request, *args, **kwargs)
        
        return wrapped_view
    
    if function:
        return decorator(function)
    return decorator


def require_permission_async(
    permission: str,
    raise_exception: bool = True
) -> Callable:
    """
    Async decorator to require a specific permission.
    
    Usage:
        @require_permission_async("posts:create")
        async def create_post_async(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapped_view(request: HttpRequest, *args, **kwargs):
            if not hasattr(request, "auth_user") or not request.auth_user:
                if raise_exception:
                    raise PermissionDenied("Authentication required")
                
                return JsonResponse(
                    {"error": "Authentication required"},
                    status=401
                )
            
            # Check permission
            # In a real implementation, this would be async
            token = getattr(request, "auth_token", None)
            if token:
                client = AuthServiceClient()
                # This should be async in production
                import asyncio
                loop = asyncio.get_event_loop()
                has_permission = await loop.run_in_executor(
                    None,
                    client.check_permission,
                    token,
                    permission
                )
                
                if not has_permission:
                    if raise_exception:
                        raise PermissionDenied(f"Permission required: {permission}")
                    
                    return JsonResponse(
                        {
                            "error": "Permission denied",
                            "required": permission
                        },
                        status=403
                    )
            
            return await view_func(request, *args, **kwargs)
        
        return wrapped_view
    
    return decorator