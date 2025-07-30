from typing import Optional, List, Dict, Any


class AuthServiceError(Exception):
    """Base exception for Auth Service errors"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.status_code = status_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.code != "UNKNOWN_ERROR":
            return f"[{self.code}] {self.message}"
        return self.message


class TokenError(AuthServiceError):
    """Token-related errors (invalid, expired, etc.)"""
    
    def __init__(self, message: str, code: str = "INVALID_TOKEN"):
        super().__init__(message, code=code, status_code=401)


class PermissionError(AuthServiceError):
    """Permission denied errors"""
    
    def __init__(
        self,
        message: str,
        required_permissions: Optional[List[str]] = None,
        code: str = "PERMISSION_DENIED",
    ):
        details = {}
        if required_permissions:
            details["required_permissions"] = required_permissions
        super().__init__(message, code=code, status_code=403, details=details)
        self.required_permissions = required_permissions or []


class NetworkError(AuthServiceError):
    """Network-related errors"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(message, code="NETWORK_ERROR", details=details)
        self.original_error = original_error


class ConfigurationError(AuthServiceError):
    """Configuration errors"""
    
    def __init__(self, message: str):
        super().__init__(message, code="CONFIGURATION_ERROR", status_code=500)


class RateLimitError(AuthServiceError):
    """Rate limit exceeded errors"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message, code="RATE_LIMIT_EXCEEDED", status_code=429, details=details
        )
        self.retry_after = retry_after


class ValidationError(AuthServiceError):
    """Validation errors"""
    
    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=validation_errors or {},
        )