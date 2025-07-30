from typing import Optional, Tuple
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework import exceptions

from ..client import AuthServiceClient
from ..config import get_config
from ..exceptions import TokenError, AuthServiceError


class AuthServiceAuthentication(authentication.BaseAuthentication):
    """
    DRF Authentication class for Auth Service.
    
    Authenticates requests using Auth Service tokens from:
    - Authorization: Bearer <token>
    - Cookie: auth_token=<token>
    
    Usage in settings.py:
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'authservice_django.drf.AuthServiceAuthentication',
            ],
        }
    """
    
    keyword = "Bearer"
    
    def __init__(self):
        self.config = get_config()
        self.client = AuthServiceClient(self.config)
    
    def authenticate(self, request) -> Optional[Tuple]:
        """
        Authenticate the request and return a two-tuple of (user, token).
        
        Args:
            request: DRF Request object
            
        Returns:
            Tuple of (user, token) if authenticated, None otherwise
        """
        # Get token from request
        token = self.get_token_from_request(request)
        
        if not token:
            return None
        
        # Authenticate with Django backend
        user = self.authenticate_credentials(token, request)
        
        # Store token for later use
        if user:
            user._auth_service_token = token
            
            # Fetch and cache permissions
            try:
                perm_data = self.client.get_user_permissions(token)
                request.auth_permissions = [
                    f"{p['resource']}:{p['action']}" 
                    for p in perm_data.get("permissions", [])
                ]
                request.auth_roles = perm_data.get("roles", [])
            except:
                request.auth_permissions = []
                request.auth_roles = []
        
        return (user, token)
    
    def authenticate_credentials(self, token: str, request=None):
        """
        Authenticate the given credentials.
        
        Args:
            token: The auth token
            request: Optional request object
            
        Returns:
            User object
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        try:
            # Use Django authentication backend
            user = authenticate(request=request, token=token)
            
            if not user:
                raise exceptions.AuthenticationFailed("Invalid token")
            
            if not user.is_active:
                raise exceptions.AuthenticationFailed("User inactive or deleted")
            
            return user
            
        except TokenError as e:
            raise exceptions.AuthenticationFailed(str(e))
        except AuthServiceError as e:
            raise exceptions.AuthenticationFailed("Authentication service error")
        except Exception as e:
            raise exceptions.AuthenticationFailed("Authentication failed")
    
    def get_token_from_request(self, request) -> Optional[str]:
        """
        Extract token from request.
        
        Checks:
        1. Authorization header
        2. Cookie
        3. Session
        
        Args:
            request: DRF Request object
            
        Returns:
            Token string if found
        """
        # Check Authorization header
        auth_header = authentication.get_authorization_header(request).decode()
        if auth_header.lower().startswith(self.keyword.lower() + ' '):
            return auth_header[len(self.keyword) + 1:]
        
        # Check cookie
        token = request.COOKIES.get("auth_token")
        if token:
            return token
        
        # Check session
        if hasattr(request, "session"):
            token = request.session.get("auth_token")
            if token:
                return token
        
        return None
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return self.keyword


class AuthServiceTokenAuthentication(AuthServiceAuthentication):
    """
    Token authentication that only checks Authorization header.
    
    This is useful for API-only endpoints where cookies/sessions
    are not used.
    """
    
    def get_token_from_request(self, request) -> Optional[str]:
        """Only check Authorization header"""
        auth_header = authentication.get_authorization_header(request).decode()
        if auth_header.lower().startswith(self.keyword.lower() + ' '):
            return auth_header[len(self.keyword) + 1:]
        return None


class AuthServiceSessionAuthentication(authentication.SessionAuthentication):
    """
    Session authentication that integrates with Auth Service.
    
    This allows using Django's session authentication while still
    checking permissions with Auth Service.
    """
    
    def __init__(self):
        super().__init__()
        self.client = AuthServiceClient()
    
    def authenticate(self, request):
        """
        Authenticate using session and enhance with Auth Service data.
        """
        # Get user from session
        result = super().authenticate(request)
        if not result:
            return None
        
        user, _ = result
        
        # Try to get auth token from session
        token = request.session.get("auth_token")
        if token:
            user._auth_service_token = token
            
            # Fetch permissions
            try:
                perm_data = self.client.get_user_permissions(token)
                request.auth_permissions = [
                    f"{p['resource']}:{p['action']}" 
                    for p in perm_data.get("permissions", [])
                ]
                request.auth_roles = perm_data.get("roles", [])
            except:
                request.auth_permissions = []
                request.auth_roles = []
        
        return (user, None)