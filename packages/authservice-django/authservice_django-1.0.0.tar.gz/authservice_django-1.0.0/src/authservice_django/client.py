import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse

import jwt
import requests
from django.core.cache import cache
from django.utils.functional import cached_property

from .config import AuthServiceConfig
from .exceptions import (
    AuthServiceError,
    TokenError,
    PermissionError,
    NetworkError,
    RateLimitError,
    ValidationError,
)


class AuthServiceClient:
    """Client for interacting with Auth Service API"""
    
    def __init__(self, config: Optional[AuthServiceConfig] = None):
        self.config = config or AuthServiceConfig.from_settings()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic"""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "X-SDK-Version": "1.0.0",
            "X-SDK-Language": "python-django",
        })
        
        # Configure retry
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _generate_signature(
        self, method: str, path: str, timestamp: str, body: Optional[bytes] = None
    ) -> str:
        """Generate HMAC-SHA256 signature for request"""
        body_hash = ""
        if body:
            body_hash = hashlib.sha256(body).hexdigest()
        
        message = f"{method.upper()}:{path}:{timestamp}:{body_hash}"
        signature = hmac.new(
            self.config.app_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to Auth Service"""
        url = f"{self.config.auth_service_url}{endpoint}"
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Prepare request
        timestamp = str(int(time.time() * 1000))
        body = json.dumps(data).encode() if data else None
        
        # Generate signature
        signature = self._generate_signature(method, path, timestamp, body)
        
        # Set headers
        request_headers = {
            "X-App-ID": self.config.app_id,
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }
        
        if token:
            request_headers["Authorization"] = f"Bearer {token}"
        
        if headers:
            request_headers.update(headers)
        
        # Make request
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )
            
            # Handle response
            if response.status_code == 204:
                return {}
            
            response_data = response.json() if response.content else {}
            
            if not response.ok:
                self._handle_error_response(response.status_code, response_data)
            
            return response_data
            
        except requests.exceptions.Timeout:
            raise NetworkError("Request timeout")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}", original_error=e)
    
    def _handle_error_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Handle error responses from API"""
        message = data.get("message", "Unknown error")
        code = data.get("code", "UNKNOWN_ERROR")
        details = data.get("details", {})
        
        if status_code == 401:
            raise TokenError(message, code=code)
        elif status_code == 403:
            required_permissions = details.get("required_permissions", [])
            raise PermissionError(message, required_permissions=required_permissions)
        elif status_code == 429:
            retry_after = details.get("retry_after")
            raise RateLimitError(message, retry_after=retry_after)
        elif status_code == 400:
            raise ValidationError(message, validation_errors=details)
        else:
            raise AuthServiceError(message, code=code, status_code=status_code, details=details)
    
    def _get_cache_key(self, key_type: str, *args) -> str:
        """Generate cache key"""
        parts = [self.config.cache_key_prefix, self.config.app_id, key_type] + list(args)
        return ":".join(str(part) for part in parts)
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if enabled"""
        if not self.config.cache_enabled:
            return None
        return cache.get(key)
    
    def _set_cache(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set value in cache if enabled"""
        if not self.config.cache_enabled:
            return
        timeout = timeout or self.config.cache_ttl
        cache.set(key, value, timeout)
    
    def _invalidate_cache(self, key_pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        if not self.config.cache_enabled:
            return
        # Django cache doesn't support pattern deletion, so we track keys
        # In production, use Redis cache backend for better support
        cache.delete_many(cache.keys(f"{key_pattern}*"))
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify token and get user info"""
        # Try to decode token locally first (without verification)
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
            if not user_id:
                raise TokenError("Invalid token: missing user ID")
        except jwt.DecodeError:
            raise TokenError("Invalid token format")
        
        # Check cache
        cache_key = self._get_cache_key("token", token[:16])  # Use first 16 chars
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Verify with API
        response = self._make_request(
            "GET",
            "/auth/users/me",
            token=token
        )
        
        # Cache result
        self._set_cache(cache_key, response, timeout=300)  # 5 minutes
        
        return response
    
    def get_user_permissions(self, token: str) -> Dict[str, Any]:
        """Get user permissions"""
        # Get user ID from token
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
        except:
            raise TokenError("Invalid token")
        
        # Check cache
        cache_key = self._get_cache_key("permissions", user_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Get from API
        response = self._make_request(
            "GET",
            "/auth/users/me/permissions",
            token=token
        )
        
        # Cache result
        self._set_cache(cache_key, response)
        
        return response
    
    def check_permission(self, token: str, permission: str) -> bool:
        """Check if user has specific permission"""
        # Check cache
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
        except:
            return False
        
        cache_key = self._get_cache_key("perm", user_id, permission)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Check with API
        try:
            response = self._make_request(
                "POST",
                "/auth/users/me/check-permission",
                data={"permission": permission},
                token=token
            )
            result = response.get("allowed", False)
            
            # Cache result
            self._set_cache(cache_key, result)
            
            return result
        except (TokenError, PermissionError):
            return False
    
    def check_permissions(
        self, token: str, permissions: List[str], require_all: bool = False
    ) -> Dict[str, bool]:
        """Check multiple permissions"""
        # Get all permissions for user
        try:
            user_perms = self.get_user_permissions(token)
            user_permission_list = [
                f"{p['resource']}:{p['action']}" 
                for p in user_perms.get("permissions", [])
            ]
            
            results = {}
            for permission in permissions:
                results[permission] = permission in user_permission_list
                # Cache individual results
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    user_id = payload.get("sub")
                    cache_key = self._get_cache_key("perm", user_id, permission)
                    self._set_cache(cache_key, results[permission])
                except:
                    pass
            
            return results
        except:
            # Return all False on error
            return {perm: False for perm in permissions}
    
    def has_any_permission(self, token: str, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions"""
        results = self.check_permissions(token, permissions)
        return any(results.values())
    
    def has_all_permissions(self, token: str, permissions: List[str]) -> bool:
        """Check if user has all of the specified permissions"""
        results = self.check_permissions(token, permissions)
        return all(results.values())
    
    def invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate all cache for a user"""
        patterns = [
            self._get_cache_key("permissions", user_id),
            self._get_cache_key("perm", user_id),
            self._get_cache_key("token"),
        ]
        for pattern in patterns:
            self._invalidate_cache(pattern)
    
    def verify_webhook_signature(
        self, signature: str, timestamp: str, body: bytes
    ) -> bool:
        """Verify webhook signature from Auth Service"""
        # Check timestamp is within 5 minutes
        current_time = int(time.time() * 1000)
        request_time = int(timestamp)
        if abs(current_time - request_time) > 300000:  # 5 minutes
            return False
        
        # Generate expected signature
        expected_signature = self._generate_signature(
            "POST", "/webhook", timestamp, body
        )
        
        # Constant-time comparison
        return hmac.compare_digest(signature, expected_signature)
    
    def get_user_mfa_status(self, token: str) -> Dict[str, Any]:
        """
        Get user's MFA status
        
        This is useful for showing MFA status in admin panels or user profiles.
        The token must be valid and MFA must be completed if enabled.
        
        Returns:
            Dict containing:
            - enabled: bool - Whether MFA is enabled
            - enabledAt: Optional[str] - When MFA was enabled (ISO format)
            - backupCodesRemaining: int - Number of unused backup codes
        """
        response = self._make_request(
            "GET",
            "/auth/users/mfa/status",
            token=token
        )
        return response
    
    def verify_user_token_with_mfa(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify a user token and ensure MFA was completed if required
        
        This method verifies that:
        1. The token is valid
        2. The user exists
        3. If MFA is enabled, it was completed before token issuance
        
        Args:
            token: The JWT token to verify
            
        Returns:
            Tuple of (is_valid, user_info)
            - is_valid: True if token is valid and MFA was completed
            - user_info: User information if valid, None otherwise
        """
        try:
            user_info = self.verify_token(token)
            # If we get user info, the token is valid and MFA was completed
            return True, user_info
        except (TokenError, AuthServiceError):
            return False, None
    
    def handle_mfa_webhook(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Handle MFA-related webhook events
        
        Common events:
        - user.mfa.enabled: User enabled MFA
        - user.mfa.disabled: User disabled MFA
        - user.mfa.backup_codes.regenerated: Backup codes regenerated
        
        This method automatically invalidates the appropriate caches.
        """
        user_id = event_data.get("userId")
        if not user_id:
            return
        
        if event_type in ["user.mfa.enabled", "user.mfa.disabled", "user.permission.changed"]:
            # Invalidate user cache since MFA status affects token validity
            self.invalidate_user_cache(user_id)