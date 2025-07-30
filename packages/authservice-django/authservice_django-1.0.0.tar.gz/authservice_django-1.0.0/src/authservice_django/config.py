from typing import Optional, Dict, Any
from django.conf import settings
from .exceptions import ConfigurationError


class AuthServiceConfig:
    """Configuration for Auth Service SDK"""
    
    def __init__(
        self,
        auth_service_url: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        cache_enabled: bool = True,
        cache_ttl: int = 300,  # 5 minutes
        cache_key_prefix: str = "authservice",
        timeout: int = 10,  # seconds
        retry_attempts: int = 3,
        retry_delay: float = 1.0,  # seconds
        verify_ssl: bool = True,
        user_model: Optional[str] = None,
        create_users: bool = True,
        update_users: bool = True,
        sync_permissions: bool = True,
    ):
        # Get from Django settings if not provided
        self.auth_service_url = auth_service_url or getattr(
            settings, "AUTH_SERVICE_URL", None
        )
        self.app_id = app_id or getattr(settings, "AUTH_SERVICE_APP_ID", None)
        self.app_secret = app_secret or getattr(
            settings, "AUTH_SERVICE_APP_SECRET", None
        )
        
        # Validate required settings
        if not self.auth_service_url:
            raise ConfigurationError("AUTH_SERVICE_URL is required")
        if not self.app_id:
            raise ConfigurationError("AUTH_SERVICE_APP_ID is required")
        if not self.app_secret:
            raise ConfigurationError("AUTH_SERVICE_APP_SECRET is required")
        
        # Ensure URL doesn't end with slash
        self.auth_service_url = self.auth_service_url.rstrip("/")
        
        # Cache settings
        self.cache_enabled = getattr(
            settings, "AUTH_SERVICE_CACHE_ENABLED", cache_enabled
        )
        self.cache_ttl = getattr(settings, "AUTH_SERVICE_CACHE_TTL", cache_ttl)
        self.cache_key_prefix = getattr(
            settings, "AUTH_SERVICE_CACHE_PREFIX", cache_key_prefix
        )
        
        # Request settings
        self.timeout = getattr(settings, "AUTH_SERVICE_TIMEOUT", timeout)
        self.retry_attempts = getattr(
            settings, "AUTH_SERVICE_RETRY_ATTEMPTS", retry_attempts
        )
        self.retry_delay = getattr(
            settings, "AUTH_SERVICE_RETRY_DELAY", retry_delay
        )
        self.verify_ssl = getattr(settings, "AUTH_SERVICE_VERIFY_SSL", verify_ssl)
        
        # User sync settings
        self.user_model = user_model or getattr(
            settings, "AUTH_SERVICE_USER_MODEL", "auth.User"
        )
        self.create_users = getattr(
            settings, "AUTH_SERVICE_CREATE_USERS", create_users
        )
        self.update_users = getattr(
            settings, "AUTH_SERVICE_UPDATE_USERS", update_users
        )
        self.sync_permissions = getattr(
            settings, "AUTH_SERVICE_SYNC_PERMISSIONS", sync_permissions
        )
        
        # Additional Django-specific settings
        self.login_url = getattr(settings, "AUTH_SERVICE_LOGIN_URL", "/login/")
        self.login_redirect_url = getattr(
            settings, "AUTH_SERVICE_LOGIN_REDIRECT_URL", "/"
        )
        self.logout_redirect_url = getattr(
            settings, "AUTH_SERVICE_LOGOUT_REDIRECT_URL", "/"
        )
        self.unauthorized_redirect_url = getattr(
            settings, "AUTH_SERVICE_UNAUTHORIZED_URL", "/unauthorized/"
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "auth_service_url": self.auth_service_url,
            "app_id": self.app_id,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "verify_ssl": self.verify_ssl,
        }
    
    @classmethod
    def from_settings(cls) -> "AuthServiceConfig":
        """Create config from Django settings"""
        return cls()


# Global config instance
_config: Optional[AuthServiceConfig] = None


def get_config() -> AuthServiceConfig:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = AuthServiceConfig.from_settings()
    return _config


def set_config(config: AuthServiceConfig) -> None:
    """Set global config instance"""
    global _config
    _config = config