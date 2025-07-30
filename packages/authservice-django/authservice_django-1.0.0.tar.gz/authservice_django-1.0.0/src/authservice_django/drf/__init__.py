"""Django REST Framework integration for Auth Service SDK"""

from .authentication import AuthServiceAuthentication
from .permissions import (
    IsAuthenticated,
    HasPermission,
    HasAnyPermission,
    HasAllPermissions,
    DjangoModelPermissions,
)
from .throttling import AuthServiceThrottle
from .views import AuthServiceAPIView, AuthServiceViewSet

__all__ = [
    # Authentication
    "AuthServiceAuthentication",
    # Permissions
    "IsAuthenticated",
    "HasPermission",
    "HasAnyPermission", 
    "HasAllPermissions",
    "DjangoModelPermissions",
    # Throttling
    "AuthServiceThrottle",
    # Views
    "AuthServiceAPIView",
    "AuthServiceViewSet",
]