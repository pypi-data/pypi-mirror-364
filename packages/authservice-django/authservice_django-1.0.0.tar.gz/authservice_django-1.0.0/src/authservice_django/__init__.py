"""
Auth Service Django SDK

A comprehensive Django integration for Auth Service providing authentication,
authorization, and permission management.
"""

__version__ = "1.0.0"
__author__ = "Auth Service Team"

from .client import AuthServiceClient
from .config import AuthServiceConfig
from .decorators import (
    require_auth,
    require_permission,
    require_any_permission,
    require_all_permissions,
)
from .middleware import AuthServiceMiddleware
from .mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    MultiplePermissionsRequiredMixin,
)
from .backends import AuthServiceBackend
from .exceptions import (
    AuthServiceError,
    TokenError,
    PermissionError,
    NetworkError,
    ConfigurationError,
)

__all__ = [
    "AuthServiceClient",
    "AuthServiceConfig",
    "AuthServiceMiddleware",
    "AuthServiceBackend",
    # Decorators
    "require_auth",
    "require_permission",
    "require_any_permission",
    "require_all_permissions",
    # Mixins
    "LoginRequiredMixin",
    "PermissionRequiredMixin",
    "MultiplePermissionsRequiredMixin",
    # Exceptions
    "AuthServiceError",
    "TokenError",
    "PermissionError",
    "NetworkError",
    "ConfigurationError",
]

# Default app config
default_app_config = "authservice_django.apps.AuthServiceConfig"