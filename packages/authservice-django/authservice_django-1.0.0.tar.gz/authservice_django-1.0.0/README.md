# Auth Service Django SDK

A comprehensive Django integration for Auth Service providing secure authentication, authorization, and permission management.

## Features

- 🔐 **Django Authentication Backend**: Seamless integration with Django's auth system
- 🛡️ **Middleware Support**: Automatic token extraction and validation
- 🎯 **Decorators & Mixins**: Easy protection for views and APIs
- 🚀 **DRF Integration**: Full Django REST Framework support
- ⚡ **Caching**: Built-in caching with Django's cache framework
- 🔄 **Async Support**: Django 4.1+ async view support
- 📊 **Type Safety**: Full type hints for better IDE support
- 🔐 **MFA Support**: Two-factor authentication integration

## Installation

```bash
pip install authservice-django
```

For Django REST Framework support:
```bash
pip install authservice-django[drf]
```

For async support:
```bash
pip install authservice-django[async]
```

## Quick Start

### 1. Configure Django Settings

```python
# settings.py

# Add to installed apps
INSTALLED_APPS = [
    # ...
    'authservice_django',
]

# Add authentication backend
AUTHENTICATION_BACKENDS = [
    'authservice_django.backends.AuthServiceBackend',
    'django.contrib.auth.backends.ModelBackend',  # Keep for admin
]

# Add middleware
MIDDLEWARE = [
    # ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'authservice_django.middleware.AuthServiceMiddleware',
]

# Auth Service configuration
AUTH_SERVICE_URL = 'https://auth.example.com'
AUTH_SERVICE_APP_ID = 'your-app-id'
AUTH_SERVICE_APP_SECRET = 'your-app-secret'

# Optional settings
AUTH_SERVICE_CACHE_ENABLED = True
AUTH_SERVICE_CACHE_TTL = 300  # 5 minutes
AUTH_SERVICE_CREATE_USERS = True  # Auto-create users
AUTH_SERVICE_UPDATE_USERS = True  # Update user info
AUTH_SERVICE_LOGIN_URL = '/login/'
AUTH_SERVICE_UNAUTHORIZED_URL = '/unauthorized/'
```

### 2. Protect Views with Decorators

```python
from authservice_django import require_auth, require_permission

@require_auth
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@require_permission('posts:create')
def create_post_view(request):
    # User has permission to create posts
    return render(request, 'create_post.html')

@require_any_permission(['posts:edit', 'posts:admin'])
def edit_post_view(request, post_id):
    # User has either edit or admin permission
    return render(request, 'edit_post.html')
```

### 3. Protect Class-Based Views

```python
from django.views.generic import CreateView, UpdateView
from authservice_django import LoginRequiredMixin, PermissionRequiredMixin

class CreatePostView(PermissionRequiredMixin, CreateView):
    model = Post
    permission_required = 'posts:create'
    template_name = 'create_post.html'

class EditPostView(PermissionRequiredMixin, UpdateView):
    model = Post
    permission_required = ['posts:edit', 'posts:admin']  # Requires all
    template_name = 'edit_post.html'
```

## Django REST Framework Integration

### Configure DRF Settings

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authservice_django.drf.AuthServiceAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'authservice_django.drf.IsAuthenticated',
    ],
}
```

### Protect API Views

```python
from rest_framework import viewsets
from authservice_django.drf import HasPermission, HasAnyPermission

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [HasPermission]
    
    def get_required_permission(self):
        """Dynamic permissions based on action"""
        if self.action == 'create':
            return 'posts:create'
        elif self.action in ['update', 'partial_update']:
            return 'posts:edit'
        elif self.action == 'destroy':
            return 'posts:delete'
        return None  # Read is allowed for authenticated users
```

### Custom Permission Classes

```python
from authservice_django.drf import BaseAuthServicePermission

class IsPostOwner(BaseAuthServicePermission):
    def has_object_permission(self, request, view, obj):
        # Check if user owns the post
        return obj.author == request.user

class CanModerate(BaseAuthServicePermission):
    def has_permission(self, request, view):
        token = self.get_auth_token(request)
        if not token:
            return False
        
        return self.client.check_permission(token, 'posts:moderate')
```

## Multi-Factor Authentication (MFA)

The Django SDK is fully MFA-aware. When users have MFA enabled, they must complete MFA verification before accessing protected resources.

### MFA Status Check

```python
from authservice_django import AuthServiceClient

@require_auth
def account_security_view(request):
    """Display user's MFA status"""
    client = AuthServiceClient()
    
    # Get MFA status - middleware ensures token is valid
    mfa_status = client.get_user_mfa_status(request.auth_token)
    
    return render(request, 'account/security.html', {
        'mfa_enabled': mfa_status['enabled'],
        'backup_codes_remaining': mfa_status.get('backupCodesRemaining', 0)
    })
```

### MFA-Protected Views

The SDK automatically enforces MFA. If a user has MFA enabled but hasn't completed it:

```python
@require_auth
def sensitive_data_view(request):
    """
    This view is automatically protected by MFA.
    Users with MFA enabled must complete verification first.
    """
    # If we reach here, user has valid auth AND completed MFA if enabled
    return render(request, 'sensitive_data.html')
```

### Handling MFA in Login Flow

```python
from authservice_django import AuthServiceClient, AuthServiceError

def custom_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        mfa_code = request.POST.get('mfa_code')
        
        client = AuthServiceClient()
        
        try:
            # Login with optional MFA code
            if mfa_code:
                # User provided MFA code
                result = client.login_user(email, password, mfa_code=mfa_code)
            else:
                # Initial login attempt
                result = client.login_user(email, password)
            
            # Success - set token in session/cookie
            request.session['auth_token'] = result['accessToken']
            return redirect('dashboard')
            
        except AuthServiceError as e:
            if e.code == 'MFA_REQUIRED':
                # User needs to provide MFA code
                return render(request, 'login.html', {
                    'show_mfa': True,
                    'email': email,
                    'error': 'Please enter your 2FA code'
                })
            else:
                # Other error
                return render(request, 'login.html', {
                    'error': str(e)
                })
    
    return render(request, 'login.html')
```

### MFA Webhook Events

```python
from django.views.decorators.csrf import csrf_exempt
from authservice_django import AuthServiceClient

@csrf_exempt
def mfa_webhook_handler(request):
    """Handle MFA-related webhook events"""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    client = AuthServiceClient()
    
    # Verify webhook signature
    signature = request.headers.get('X-Auth-Signature')
    timestamp = request.headers.get('X-Auth-Timestamp')
    
    if not client.verify_webhook_signature(signature, timestamp, request.body):
        return HttpResponse(status=401)
    
    event = json.loads(request.body)
    event_type = event.get('type')
    event_data = event.get('data', {})
    
    # Handle MFA events
    if event_type == 'user.mfa.enabled':
        # User enabled MFA
        user_id = event_data['userId']
        # Send congratulatory email
        send_mfa_enabled_email(user_id)
        # Log security event
        log_security_event('mfa_enabled', user_id)
        
    elif event_type == 'user.mfa.disabled':
        # User disabled MFA - security concern
        user_id = event_data['userId']
        # Send warning email
        send_mfa_disabled_warning(user_id)
        # Log security event
        log_security_event('mfa_disabled', user_id)
        
    elif event_type == 'user.mfa.backup_codes.regenerated':
        # Backup codes regenerated
        user_id = event_data['userId']
        # Log for audit trail
        log_security_event('backup_codes_regenerated', user_id)
    
    # Let SDK handle cache invalidation
    client.handle_mfa_webhook(event_type, event_data)
    
    return HttpResponse(status=200)
```

### MFA in Templates

```django
{# security_settings.html #}
{% load authservice_tags %}

<h2>Two-Factor Authentication</h2>

{% if mfa_enabled %}
    <div class="alert alert-success">
        <strong>2FA is enabled</strong>
        <p>Your account is protected with two-factor authentication.</p>
        <p>Backup codes remaining: {{ backup_codes_remaining }}</p>
    </div>
    
    <div class="actions">
        <a href="{% url 'regenerate-backup-codes' %}" class="btn btn-secondary">
            Regenerate Backup Codes
        </a>
        <a href="{% url 'disable-mfa' %}" class="btn btn-danger">
            Disable 2FA
        </a>
    </div>
{% else %}
    <div class="alert alert-warning">
        <strong>2FA is not enabled</strong>
        <p>Add an extra layer of security to your account.</p>
    </div>
    
    <a href="{% url 'setup-mfa' %}" class="btn btn-primary">
        Enable Two-Factor Authentication
    </a>
{% endif %}
```

### MFA Best Practices

1. **Always use MFA for admin/privileged users**
2. **Provide clear instructions during MFA setup**
3. **Store backup codes securely**
4. **Log all MFA-related events for security auditing**
5. **Send notifications when MFA status changes**
6. **Consider requiring MFA for sensitive operations**
7. **Test MFA flow thoroughly including edge cases**

### MFA Error Handling

```python
from authservice_django import AuthServiceError

try:
    # MFA operations
    mfa_status = client.get_user_mfa_status(token)
except AuthServiceError as e:
    if e.code == 'TOKEN_EXPIRED':
        # Token expired - redirect to login
        return redirect('login')
    elif e.code == 'MFA_REQUIRED':
        # MFA verification needed
        return redirect('mfa-verify')
    else:
        # Handle other errors
        logger.error(f"MFA error: {e}")
        return render(request, 'error.html')
```

## Advanced Usage

### Custom User Model

```python
# models.py
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    auth_service_id = models.CharField(max_length=255, unique=True)
    # ... other fields

# settings.py
AUTH_USER_MODEL = 'myapp.CustomUser'
AUTH_SERVICE_USER_MODEL = 'myapp.CustomUser'
```

### Permission Mapping

Map Auth Service permissions to Django permissions:

```python
# settings.py
AUTH_SERVICE_PERMISSION_MAP = {
    'posts:create': 'blog.add_post',
    'posts:edit': 'blog.change_post',
    'posts:delete': 'blog.delete_post',
    'posts:read': 'blog.view_post',
}
```

### Webhook Integration

```python
from authservice_django import AuthServiceClient

def webhook_view(request):
    client = AuthServiceClient()
    
    # Verify webhook signature
    signature = request.headers.get('X-Webhook-Signature')
    timestamp = request.headers.get('X-Webhook-Timestamp')
    
    if not client.verify_webhook_signature(
        signature, timestamp, request.body
    ):
        return HttpResponse(status=401)
    
    # Process webhook
    data = json.loads(request.body)
    if data['event'] == 'permission.changed':
        # Invalidate cache for user
        client.invalidate_user_cache(data['userId'])
    
    return HttpResponse(status=200)
```

### Async Views (Django 4.1+)

```python
from authservice_django import require_auth_async, require_permission_async

@require_auth_async
async def async_profile_view(request):
    # Async view with authentication
    return JsonResponse({'user_id': request.auth_user['id']})

@require_permission_async('posts:create')
async def async_create_post(request):
    # Async view with permission check
    data = await request.json()
    # ... create post
    return JsonResponse({'status': 'created'})
```

### Template Tags

```django
{% load authservice_tags %}

{% if user|has_permission:"posts:create" %}
    <a href="{% url 'create_post' %}">Create Post</a>
{% endif %}

{% if user|has_any_permission:"posts:edit,posts:admin" %}
    <a href="{% url 'edit_post' post.id %}">Edit</a>
{% endif %}

{% if user|has_role:"moderator" %}
    <div class="moderation-tools">...</div>
{% endif %}
```

### Management Commands

```bash
# Sync permissions from Auth Service
python manage.py sync_auth_permissions

# Clear auth cache
python manage.py clear_auth_cache

# Verify auth service connection
python manage.py check_auth_service
```

## Caching

The SDK uses Django's cache framework. Configure caching in settings:

```python
# Use Redis for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache settings
AUTH_SERVICE_CACHE_ENABLED = True
AUTH_SERVICE_CACHE_TTL = 300  # 5 minutes
AUTH_SERVICE_CACHE_PREFIX = 'authservice'
```

## Error Handling

```python
from authservice_django import (
    AuthServiceError,
    TokenError,
    PermissionError,
    NetworkError
)

try:
    # Your auth code
except TokenError as e:
    # Invalid or expired token
    logger.error(f"Token error: {e}")
except PermissionError as e:
    # Permission denied
    logger.warning(f"Permission denied: {e.required_permissions}")
except NetworkError as e:
    # Network/connection issues
    logger.error(f"Network error: {e}")
except AuthServiceError as e:
    # General auth service error
    logger.error(f"Auth error: {e.code} - {e.message}")
```

## Testing

### Mock Authentication in Tests

```python
from django.test import TestCase, Client
from authservice_django.testing import AuthServiceTestMixin

class PostViewTests(AuthServiceTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.create_test_user(
            permissions=['posts:create', 'posts:edit']
        )
    
    def test_create_post_with_permission(self):
        self.authenticate_user(self.user)
        response = self.client.post('/posts/create/', {
            'title': 'Test Post',
            'content': 'Test content'
        })
        self.assertEqual(response.status_code, 201)
    
    def test_create_post_without_permission(self):
        user = self.create_test_user(permissions=[])
        self.authenticate_user(user)
        response = self.client.post('/posts/create/', {
            'title': 'Test Post',
            'content': 'Test content'
        })
        self.assertEqual(response.status_code, 403)
```

### Test Settings

```python
# test_settings.py
from .settings import *

# Disable auth service for tests
AUTH_SERVICE_URL = 'http://mock-auth-service'
AUTH_SERVICE_CACHE_ENABLED = False

# Use in-memory cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

## Debugging

Enable debug logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'authservice_django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Best Practices

1. **Always use HTTPS** for AUTH_SERVICE_URL in production
2. **Keep APP_SECRET secure** - use environment variables
3. **Enable caching** for better performance
4. **Use specific permissions** rather than broad ones
5. **Implement proper error handling** for network failures
6. **Regular cache invalidation** for permission changes
7. **Monitor auth service health** and response times

## Migration from Django Auth

```python
# management/commands/migrate_to_authservice.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authservice_django import AuthServiceClient

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        client = AuthServiceClient()
        
        for user in User.objects.all():
            # Create user in auth service
            # Map Django permissions to Auth Service
            # Update user with auth_service_id
            pass
```

## Troubleshooting

### Common Issues

1. **"AUTH_SERVICE_URL is required"**
   - Ensure AUTH_SERVICE_URL is set in settings.py
   - Check for typos in environment variables

2. **Permission always denied**
   - Verify token is being passed correctly
   - Check permission format (resource:action)
   - Ensure user has permission in Auth Service

3. **Users not created automatically**
   - Set AUTH_SERVICE_CREATE_USERS = True
   - Ensure User model has required fields

4. **Cache not working**
   - Verify cache backend is configured
   - Check AUTH_SERVICE_CACHE_ENABLED = True
   - Monitor cache hit/miss rates

## License

MIT