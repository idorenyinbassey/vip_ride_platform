# JWT Authentication System Documentation

## Overview

This is a comprehensive JWT authentication system for the VIP Ride-Hailing Platform, featuring tier-based security, multi-factor authentication, and advanced security measures.

## Features

### Core Authentication
- **JWT Tokens**: Access tokens (15min-1hour) and refresh tokens (7-30 days)
- **Token Rotation**: Automatic token refresh with blacklisting of old tokens
- **Tier-Based Security**: Different security levels for normal, premium, VIP, and concierge users
- **Multi-Factor Authentication**: TOTP, SMS, email, and backup codes
- **Device Management**: Trusted device tracking and verification

### Security Features
- **Rate Limiting**: Tier-based API rate limiting
- **Geolocation Control**: Location-based access restrictions
- **Session Management**: Concurrent session tracking and control
- **Security Monitoring**: Comprehensive logging and event tracking
- **Device Fingerprinting**: Enhanced device identification
- **IP Whitelisting**: Location-based access control

## API Endpoints

### Authentication
```
POST /api/auth/login/          - Login with email/password + MFA
POST /api/auth/logout/         - Logout and blacklist tokens
POST /api/auth/refresh/        - Refresh access token
POST /api/auth/register/       - User registration
```

### Security Management
```
GET  /api/auth/security/status/     - Get security status
POST /api/auth/security/logout-all/ - Force logout all sessions
```

### Multi-Factor Authentication
```
GET  /api/auth/mfa/setup/      - Get MFA status and methods
POST /api/auth/mfa/setup/      - Setup new MFA method
POST /api/auth/mfa/verify/     - Verify MFA token
DELETE /api/auth/mfa/setup/    - Disable MFA method
```

### User Profile
```
GET  /api/auth/profile/        - Get user profile
PUT  /api/auth/profile/        - Update user profile
POST /api/auth/password/change/ - Change password
```

### Device Management
```
GET  /api/auth/devices/        - List trusted devices
POST /api/auth/devices/        - Manage device trust
```

## User Tiers and Security Levels

### Normal Users
- **Access Token**: 15 minutes
- **Refresh Token**: 7 days
- **MFA**: Optional
- **Rate Limit**: 100 requests/hour
- **Sessions**: 2 concurrent

### Premium Users
- **Access Token**: 20 minutes
- **Refresh Token**: 14 days
- **MFA**: Recommended
- **Rate Limit**: 200 requests/hour
- **Sessions**: 3 concurrent

### VIP Users
- **Access Token**: 30 minutes
- **Refresh Token**: 30 days
- **MFA**: Required
- **Rate Limit**: 500 requests/hour
- **Sessions**: 5 concurrent
- **Additional**: Geolocation restrictions, device verification

### Concierge Users
- **Access Token**: 1 hour
- **Refresh Token**: 30 days
- **MFA**: Required (enhanced)
- **Rate Limit**: 1000 requests/hour
- **Sessions**: 10 concurrent
- **Additional**: All VIP features + admin capabilities

## Installation and Setup

### 1. Install Dependencies
```bash
pip install djangorestframework-simplejwt
pip install pyotp
pip install django-redis
pip install django-cors-headers
```

### 2. Update Django Settings
Add to your `settings.py`:
```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
]

# Import JWT settings
from accounts.jwt_settings import *
```

### 3. Include URLs
Add to your main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs
    path('api/auth/', include('accounts.urls')),
]
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Environment Variables
Set required environment variables:
```bash
export JWT_SECRET_KEY="your-super-secret-jwt-key"
export REDIS_URL="redis://127.0.0.1:6379/1"
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-email-password"
export TWILIO_ACCOUNT_SID="your-twilio-sid"
export TWILIO_AUTH_TOKEN="your-twilio-token"
```

## Usage Examples

### Login with MFA
```javascript
// 1. Initial login attempt
const loginResponse = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'userpassword'
    })
});

// 2. If MFA required, login again with MFA token
if (loginResponse.mfa_required) {
    const mfaResponse = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: 'user@example.com',
            password: 'userpassword',
            mfa_token: '123456'
        })
    });
}
```

### Token Refresh
```javascript
const refreshResponse = await fetch('/api/auth/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        refresh: 'your-refresh-token'
    })
});
```

### Setup TOTP MFA
```javascript
// 1. Initiate TOTP setup
const setupResponse = await fetch('/api/auth/mfa/setup/', {
    method: 'POST',
    headers: { 
        'Authorization': 'Bearer your-access-token',
        'Content-Type': 'application/json' 
    },
    body: JSON.stringify({
        method: 'totp'
    })
});

// 2. Display QR code to user
const { qr_uri } = setupResponse.data;

// 3. Verify TOTP token
const verifyResponse = await fetch('/api/auth/mfa/verify/', {
    method: 'POST',
    headers: { 
        'Authorization': 'Bearer your-access-token',
        'Content-Type': 'application/json' 
    },
    body: JSON.stringify({
        method: 'totp',
        token: '123456'
    })
});
```

## Security Considerations

### Token Security
- Use HTTPS in production
- Store tokens securely (httpOnly cookies recommended)
- Implement proper CORS configuration
- Rotate refresh tokens on each use

### MFA Implementation
- Enforce MFA for VIP and Concierge users
- Use backup codes for account recovery
- Implement rate limiting on MFA attempts
- Log all MFA events for auditing

### Device Management
- Track device fingerprints
- Allow users to manage trusted devices
- Implement device verification for new logins
- Automatic device trust expiration

### Rate Limiting
- Implement tier-based rate limits
- Use Redis for distributed rate limiting
- Apply burst allowances for peak usage
- Progressive blocking for repeated violations

## Monitoring and Logging

### Security Events
The system logs various security events:
- Failed login attempts
- Suspicious login patterns
- MFA bypass attempts
- Rate limit violations
- Unusual location access

### Log Files
- `logs/django.log`: General application logs
- `logs/security.log`: Security-specific events

### Metrics to Monitor
- Failed login rate
- MFA adoption rate
- Token refresh patterns
- Device trust violations
- Geographic access patterns

## Troubleshooting

### Common Issues

1. **Token Expired Errors**
   - Check token lifetime configuration
   - Ensure proper token rotation
   - Verify system clock synchronization

2. **MFA Verification Failures**
   - Check TOTP time window settings
   - Verify backup code storage
   - Ensure proper secret key handling

3. **Rate Limiting Issues**
   - Verify Redis connectivity
   - Check rate limit configuration
   - Monitor cache key expiration

4. **Device Verification Problems**
   - Check device fingerprint generation
   - Verify trusted device storage
   - Review device trust policies

## Production Deployment

### Security Checklist
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure proper CORS origins
- [ ] Set up Redis with authentication
- [ ] Enable security headers
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Review and update secret keys
- [ ] Test MFA flows thoroughly
- [ ] Configure backup and recovery

### Performance Optimization
- Use Redis clustering for high availability
- Implement database connection pooling
- Configure proper caching strategies
- Optimize JWT token size
- Use CDN for static assets

## Contributing

When contributing to this authentication system:

1. Follow security best practices
2. Add comprehensive tests
3. Update documentation
4. Review security implications
5. Test with different user tiers
6. Verify MFA flows work correctly

## License

This authentication system is part of the VIP Ride-Hailing Platform and follows the project's licensing terms.
