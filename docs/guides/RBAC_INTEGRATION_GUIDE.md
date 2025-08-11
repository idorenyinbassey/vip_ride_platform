# RBAC System Integration Guide

This guide explains how to integrate the role-based access control (RBAC) system into your VIP ride-hailing platform.

## Overview

The RBAC system provides:
- ✅ Custom Django permissions for each user tier (normal/premium/vip/concierge/admin)
- ✅ API endpoint protection by user role with inheritance hierarchy
- ✅ VIP data access restricted to concierge+ staff only
- ✅ Comprehensive audit logging for all permission checks
- ✅ MFA requirement enforcement for sensitive operations
- ✅ Security monitoring and threat detection

## Quick Start

### 1. Apply Database Migrations

```bash
# Create and apply migrations for new models
python manage.py makemigrations accounts
python manage.py migrate
```

### 2. Setup RBAC Permissions and Groups

```bash
# Run the RBAC setup command
python manage.py setup_rbac

# This creates:
# - 24 custom permissions for platform features
# - 5 user tier groups (normal_users, premium_users, etc.)
# - Proper permission assignments to groups
```

### 3. Add RBAC Middleware to Settings

Add to your `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Add RBAC middleware AFTER authentication
    'accounts.rbac_middleware.RBACauditMiddleware',
    'accounts.rbac_middleware.SecurityMonitoringMiddleware',
]
```

### 4. Update DRF Settings

Add to your `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'accounts.permissions.AuditedTierPermission',
    ],
    # ... other settings
}
```

### 5. Test the System

```bash
# Create test users and run all tests
python manage.py test_rbac --test-type=all --create-test-users --verbose

# Test specific components
python manage.py test_rbac --test-type=permissions
python manage.py test_rbac --test-type=audit
python manage.py test_rbac --test-type=mfa
```

## Using RBAC in Your Views

### API View Protection

```python
from rest_framework.decorators import api_view, permission_classes
from accounts.permissions import IsVIPUser, VIPDataAccessPermission, EnhancedMFAPermission

# Tier-based protection
@api_view(['GET'])
@permission_classes([IsVIPUser])
def vip_only_endpoint(request):
    """Only VIP, concierge, and admin users can access"""
    return Response({'message': 'VIP content'})

# VIP data access (concierge+ only)
@api_view(['GET'])
@permission_classes([VIPDataAccessPermission])
def vip_data_endpoint(request):
    """Only concierge and admin can access VIP user data"""
    return Response({'vip_data': 'sensitive information'})

# MFA required for sensitive operations
@api_view(['POST'])
@permission_classes([EnhancedMFAPermission])
def sensitive_operation(request):
    """Requires verified MFA token"""
    return Response({'message': 'Sensitive operation completed'})
```

### Class-Based Views

```python
from rest_framework.viewsets import ModelViewSet
from accounts.permissions import IsPremiumUser, AuditedTierPermission

class LuxuryVehicleViewSet(ModelViewSet):
    """Premium+ users can access luxury vehicles"""
    permission_classes = [IsPremiumUser, AuditedTierPermission]
    
    def get_queryset(self):
        # Your queryset logic
        pass
```

### Function-Based Views

```python
from django.contrib.auth.decorators import login_required
from accounts.permissions import check_tier_permission

@login_required
def hotel_booking_view(request):
    """Premium+ users can book hotels"""
    if not check_tier_permission(request.user, 'premium'):
        return HttpResponseForbidden('Premium subscription required')
    
    # Your view logic
    pass
```

## User Tier Hierarchy

The system uses inheritance-based permissions:

```
admin (Level 5)
  └── concierge (Level 4)
      └── vip (Level 3)
          └── premium (Level 2)
              └── normal (Level 1)
```

**Access Rules:**
- `IsNormalUser`: All authenticated users
- `IsPremiumUser`: Premium, VIP, concierge, admin
- `IsVIPUser`: VIP, concierge, admin
- `IsConciergeUser`: Concierge, admin
- `IsAdminUser`: Admin only

## Permission Classes Available

### Tier-Based Permissions
- `IsNormalUser` - All authenticated users
- `IsPremiumUser` - Premium tier and above
- `IsVIPUser` - VIP tier and above
- `IsConciergeUser` - Concierge and admin only
- `IsAdminUser` - Admin only

### Special Permissions
- `VIPDataAccessPermission` - Concierge+ only, for accessing VIP user data
- `EnhancedMFAPermission` - Requires verified MFA token
- `AuditedTierPermission` - Logs all permission checks

### Custom Permissions Created
The system creates 24 custom permissions:
- `ride_request`, `ride_cancel`, `ride_history`
- `luxury_vehicles`, `hotel_booking`, `priority_support`
- `encrypted_gps`, `sos_emergency`, `trusted_drivers`
- `vip_data_access`, `emergency_response`, `driver_management`
- `system_configuration`, `user_management`, `financial_operations`
- And more...

## Audit Logging

All permission checks are automatically logged to the `SecurityEvent` model:

```python
# View recent audit events
from accounts.models import SecurityEvent

# Get permission check events
permission_events = SecurityEvent.objects.filter(
    event_type='permission_check'
).order_by('-created_at')

# Get VIP data access events
vip_access_events = SecurityEvent.objects.filter(
    event_category='vip_data_access'
).order_by('-created_at')

# Get security alerts
security_alerts = SecurityEvent.objects.filter(
    event_category='security_alert'
).order_by('-created_at')
```

## MFA Integration

### Setting Up MFA for Users

```python
from accounts.models import MFAToken

# Create TOTP token for user
mfa_token = MFAToken.objects.create(
    user=user,
    token_type='totp',
    secret_key='generated-secret-key',
    is_verified=False
)

# Verify MFA token
mfa_token.verify_token('123456')  # User's TOTP code
```

### Checking MFA Status

```python
from accounts.permissions import has_valid_mfa

# Check if user has valid MFA
if has_valid_mfa(request.user):
    # Allow sensitive operation
    pass
else:
    # Require MFA setup/verification
    pass
```

## Security Monitoring

The security monitoring middleware automatically:
- Tracks failed login attempts
- Monitors suspicious activity patterns
- Logs VIP user request patterns
- Detects potential security threats
- Alerts on privilege escalation attempts

### Viewing Security Events

```python
# Get suspicious activity alerts
suspicious_events = SecurityEvent.objects.filter(
    event_category='suspicious_activity'
)

# Get failed authentication attempts
auth_failures = SecurityEvent.objects.filter(
    event_type='authentication_failure'
)

# Get rate limiting violations
rate_limit_events = SecurityEvent.objects.filter(
    event_type='rate_limit_exceeded'
)
```

## Configuration Options

### Audit Settings

```python
RBAC_AUDIT_SETTINGS = {
    'ENABLE_AUDIT_LOGGING': True,
    'LOG_SUCCESSFUL_REQUESTS': True,
    'LOG_FAILED_REQUESTS': True,
    'LOG_PERMISSION_CHECKS': True,
    'LOG_MFA_EVENTS': True,
    'LOG_VIP_DATA_ACCESS': True,
    'SANITIZE_REQUEST_DATA': True,
    'MAX_REQUEST_BODY_SIZE': 1024 * 10,  # 10KB
    'AUDIT_RETENTION_DAYS': 90,
}
```

### Security Settings

```python
RBAC_SECURITY_SETTINGS = {
    'ENABLE_SUSPICIOUS_ACTIVITY_DETECTION': True,
    'MAX_FAILED_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 300,  # 5 minutes
    'RATE_LIMIT_THRESHOLD': 100,  # requests per minute
    'ENABLE_IP_BLOCKING': True,
    'MONITOR_VIP_REQUESTS': True,
    'ALERT_ON_PRIVILEGE_ESCALATION': True,
}
```

### MFA Settings

```python
RBAC_MFA_SETTINGS = {
    'ENABLE_MFA': True,
    'MFA_REQUIRED_FOR_TIERS': ['vip', 'concierge', 'admin'],
    'MFA_REQUIRED_FOR_OPERATIONS': [
        'sensitive_data_access',
        'financial_operations',
        'user_management',
        'system_configuration',
    ],
    'TOTP_VALIDITY_PERIOD': 300,  # 5 minutes
    'FORCE_MFA_SETUP_ON_FIRST_LOGIN': True,
}
```

## Production Deployment

### 1. Environment Variables

```bash
# Set in your production environment
export DJANGO_SECRET_KEY='your-secret-key'
export JWT_SECRET_KEY='your-jwt-secret'
export DATABASE_URL='postgresql://...'
export REDIS_URL='redis://...'
```

### 2. Create Logs Directory

```bash
mkdir -p logs
chmod 755 logs
```

### 3. Setup Log Rotation

```bash
# Add to /etc/logrotate.d/django-rbac
/path/to/your/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 4. Monitor Security Events

Set up alerts for:
- Multiple failed authentication attempts
- Privilege escalation attempts
- Suspicious VIP data access patterns
- Rate limiting violations
- Unusual request patterns

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   ```bash
   # Check if RBAC groups were created
   python manage.py shell -c "from django.contrib.auth.models import Group; print(Group.objects.all())"
   
   # Re-run RBAC setup
   python manage.py setup_rbac
   ```

2. **Audit Events Not Logging**
   ```bash
   # Check middleware order in settings
   # Ensure RBAC middleware comes after authentication
   
   # Check SecurityEvent model migration
   python manage.py showmigrations accounts
   ```

3. **MFA Not Working**
   ```bash
   # Check MFA settings
   python manage.py shell -c "from django.conf import settings; print(getattr(settings, 'RBAC_MFA_SETTINGS', 'Not configured'))"
   
   # Verify MFA tokens
   python manage.py test_rbac --test-type=mfa --verbose
   ```

### Debug Mode

Enable verbose logging in settings:

```python
LOGGING['loggers']['rbac_audit']['level'] = 'DEBUG'
LOGGING['loggers']['security']['level'] = 'DEBUG'
```

## Next Steps

1. **Apply RBAC to existing API endpoints**
2. **Setup production monitoring and alerting**
3. **Configure automated security responses**
4. **Implement MFA for all VIP+ users**
5. **Setup audit log analysis and reporting**

## Support

The RBAC system is now fully implemented and ready for production use. All requested features have been delivered:

✅ Custom Django permissions for each user tier
✅ API endpoint protection by user role
✅ VIP data access restricted to concierge staff
✅ Audit logging for all permission checks
✅ MFA requirement for sensitive operations

The system provides enterprise-grade security and audit capabilities for your VIP ride-hailing platform.
