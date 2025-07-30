from typing import Optional, Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

from .client import AuthServiceClient
from .config import get_config
from .exceptions import TokenError, AuthServiceError


class AuthServiceMiddleware(MiddlewareMixin):
    """
    Django middleware for Auth Service authentication.
    
    This middleware:
    1. Extracts auth tokens from requests
    2. Authenticates users with Auth Service
    3. Attaches user and permission info to requests
    """
    
    def __init__(self, get_response: Optional[Callable] = None):
        super().__init__(get_response)
        self.config = get_config()
        self.client = AuthServiceClient(self.config)
        
        # Paths that don't require authentication
        self.public_paths = [
            "/login/",
            "/logout/",
            "/signup/",
            "/password-reset/",
            "/static/",
            "/media/",
            "/favicon.ico",
        ]
        
        # API paths (return JSON errors instead of redirects)
        self.api_paths = [
            "/api/",
            "/rest/",
            "/graphql/",
        ]
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process incoming request to extract and validate auth token.
        
        This middleware is MFA-aware: tokens are only issued after MFA verification
        if the user has MFA enabled, so any valid token means MFA was completed.
        
        Args:
            request: The Django request object
        
        Returns:
            None to continue processing, or HttpResponse to short-circuit
        """
        # Skip auth for public paths
        if self._is_public_path(request.path):
            return None
        
        # Extract token
        token = self._extract_token(request)
        
        if token:
            # Authenticate with token
            user = authenticate(request, token=token)
            
            if user:
                # Log user in (sets request.user)
                login(request, user, backend="authservice_django.backends.AuthServiceBackend")
                
                # Store token for later use
                request.auth_token = token
                request.user._auth_service_token = token
                
                # Fetch and cache permissions
                try:
                    perm_data = self.client.get_user_permissions(token)
                    request.user_permissions = [
                        f"{p['resource']}:{p['action']}" 
                        for p in perm_data.get("permissions", [])
                    ]
                    request.user_roles = perm_data.get("roles", [])
                except:
                    request.user_permissions = []
                    request.user_roles = []
            else:
                # Invalid token
                request.user = AnonymousUser()
                
                # Return error for API requests
                if self._is_api_path(request.path):
                    return JsonResponse(
                        {"error": "Invalid authentication token"},
                        status=401
                    )
        else:
            # No token
            request.user = AnonymousUser()
        
        return None
    
    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: tuple,
        view_kwargs: dict
    ) -> Optional[HttpResponse]:
        """
        Process view to check authentication requirements.
        
        Args:
            request: The Django request object
            view_func: The view function
            view_args: View positional arguments
            view_kwargs: View keyword arguments
        
        Returns:
            None to continue processing, or HttpResponse to short-circuit
        """
        # Check if view requires authentication
        requires_auth = getattr(view_func, "_auth_required", False)
        required_permissions = getattr(view_func, "_required_permissions", [])
        
        if requires_auth and not request.user.is_authenticated:
            # Redirect to login or return 401
            if self._is_api_path(request.path):
                return JsonResponse(
                    {"error": "Authentication required"},
                    status=401
                )
            else:
                login_url = self.config.login_url
                return redirect(f"{login_url}?next={request.path}")
        
        if required_permissions and request.user.is_authenticated:
            # Check permissions
            has_permission = self._check_permissions(
                request,
                required_permissions,
                getattr(view_func, "_require_all_permissions", False)
            )
            
            if not has_permission:
                if self._is_api_path(request.path):
                    return JsonResponse(
                        {
                            "error": "Permission denied",
                            "required": required_permissions
                        },
                        status=403
                    )
                else:
                    return redirect(self.config.unauthorized_redirect_url)
        
        return None
    
    def _extract_token(self, request: HttpRequest) -> Optional[str]:
        """
        Extract auth token from request.
        
        Checks in order:
        1. Authorization header (Bearer token)
        2. Cookie
        3. Session
        4. Query parameter (for special cases)
        
        Args:
            request: The Django request object
        
        Returns:
            Token string if found, None otherwise
        """
        # Check Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        # Check cookie
        token = request.COOKIES.get("auth_token")
        if token:
            return token
        
        # Check session
        token = request.session.get("auth_token")
        if token:
            return token
        
        # Check query parameter (only for special cases like OAuth callbacks)
        if request.method == "GET" and "token" in request.GET:
            return request.GET["token"]
        
        return None
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require auth)"""
        return any(path.startswith(public) for public in self.public_paths)
    
    def _is_api_path(self, path: str) -> bool:
        """Check if path is an API endpoint"""
        return any(path.startswith(api) for api in self.api_paths)
    
    def _check_permissions(
        self,
        request: HttpRequest,
        required_permissions: list,
        require_all: bool = False
    ) -> bool:
        """
        Check if user has required permissions.
        
        Args:
            request: The Django request object
            required_permissions: List of required permissions
            require_all: Whether all permissions are required (AND) or any (OR)
        
        Returns:
            True if user has required permissions, False otherwise
        """
        if not hasattr(request, "user_permissions"):
            return False
        
        user_permissions = set(request.user_permissions)
        required_set = set(required_permissions)
        
        if require_all:
            # User must have all permissions
            return required_set.issubset(user_permissions)
        else:
            # User must have at least one permission
            return bool(required_set.intersection(user_permissions))


class AuthServiceAPIMiddleware:
    """
    Async middleware for Django 4.1+ ASGI applications.
    
    This is a lightweight version optimized for API endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.config = get_config()
        self.client = AuthServiceClient(self.config)
    
    async def __call__(self, request):
        # Extract token
        token = self._extract_token(request)
        
        if token:
            # Verify token (simplified for async)
            try:
                user_data = await self._verify_token_async(token)
                request.auth_user = user_data
                request.auth_token = token
            except:
                request.auth_user = None
                request.auth_token = None
        else:
            request.auth_user = None
            request.auth_token = None
        
        response = await self.get_response(request)
        return response
    
    def _extract_token(self, request):
        """Extract token from request"""
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None
    
    async def _verify_token_async(self, token: str):
        """Verify token asynchronously"""
        # For now, use sync client in thread pool
        # In production, use httpx for async requests
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.client.verify_token,
            token
        )