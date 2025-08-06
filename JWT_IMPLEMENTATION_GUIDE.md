# JWT Authentication System - Implementation Guide

## 🚀 **System Overview**

The VIP Ride-Hailing Platform now has a complete JWT authentication system with advanced security features including:

- **Tier-based JWT tokens** with different lifetimes
- **Multi-factor authentication (MFA)** for VIP users
- **Token rotation** on each refresh
- **Rate limiting** based on user tier
- **Device fingerprinting** and trust management
- **Comprehensive security logging**

## 📋 **Prerequisites**

### Required Dependencies
```bash
pip install djangorestframework-simplejwt==5.5.1
pip install pyotp==2.9.0
pip install django-redis==5.4.0
pip install django-cors-headers==4.3.1
```

### Environment Variables
Create a `.env` file with:
```env
JWT_SECRET_KEY=your-super-secret-jwt-key-here
REDIS_URL=redis://127.0.0.1:6379/1
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_FROM_NUMBER=+1234567890
```

## 🔧 **Configuration**

### 1. Update Django Settings

Add to your main `settings.py`:

```python
# Import JWT settings
from accounts.jwt_settings import *

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'accounts',
]

# Update AUTH_USER_MODEL
AUTH_USER_MODEL = 'accounts.User'
```

### 2. Update URL Configuration

In your main `urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    # ... other URLs
]
```

## 🔐 **Authentication Endpoints**

### **Login with MFA Support**
```
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password",
    "device_fingerprint": "optional_device_id",
    "remember_device": false,
    "mfa_token": "123456"  // Required for VIP users
}
```

**Response (Success):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid-here",
        "email": "user@example.com",
        "tier": "vip",
        "first_name": "John",
        "last_name": "Doe"
    },
    "mfa_verified": true,
    "device_trusted": false
}
```

**Response (MFA Required):**
```json
{
    "mfa_required": true,
    "mfa_methods": ["totp", "sms", "email"],
    "message": "Multi-factor authentication required."
}
```

### **Token Refresh with Rotation**
```
POST /api/v1/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "device_fingerprint": "optional_device_id"
}
```

### **User Registration**
```
POST /api/v1/auth/register/
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+2348012345678",
    "tier": "normal"
}
```

### **MFA Setup**
```
POST /api/v1/auth/mfa/setup/
Authorization: Bearer your_access_token

{
    "method": "totp",  // Options: totp, sms, email, backup
    "phone_number": "+2348012345678"  // Required for SMS
}
```

**TOTP Response:**
```json
{
    "method": "totp",
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_uri": "otpauth://totp/VIP%20Ride%20Platform:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=VIP%20Ride%20Platform",
    "message": "TOTP setup initiated. Scan QR code."
}
```

### **Device Management**
```
POST /api/v1/auth/devices/
Authorization: Bearer your_access_token

{
    "device_fingerprint": "abc123def456",
    "device_name": "iPhone 15 Pro",
    "action": "trust"  // Options: trust, untrust, remove
}
```

## 🛡️ **Security Features**

### **Tier-Based Token Lifetimes**

| Tier | Access Token | Refresh Token | Rate Limit |
|------|-------------|---------------|------------|
| Normal | 15 minutes | 7 days | 100/hour |
| Premium | 20 minutes | 14 days | 200/hour |
| VIP | 30 minutes | 30 days | 500/hour |
| Concierge | 1 hour | 30 days | 1000/hour |

### **MFA Requirements**

- **VIP Users**: MFA always required
- **Premium Users**: MFA required for sensitive operations
- **Normal Users**: MFA optional

### **Supported MFA Methods**

1. **TOTP (Time-based One-Time Password)**
   - Compatible with Google Authenticator, Authy
   - 6-digit codes, 30-second window

2. **SMS Verification**
   - Delivered via Twilio
   - 6-digit codes, 5-minute validity

3. **Email Verification**
   - Backup method for TOTP
   - 6-digit codes, 5-minute validity

4. **Backup Codes**
   - 10 single-use codes
   - For account recovery

### **Device Trust Management**

- **Device Fingerprinting**: Based on browser characteristics
- **Trust Levels**: Basic, High, VIP
- **Automatic Expiry**: 30 days (configurable)
- **Usage Tracking**: Login frequency and patterns

## 🔒 **Security Middleware**

### **Rate Limiting**
- IP-based for anonymous users
- User-based for authenticated users
- Progressive blocking for violations

### **Security Headers**
- Content Security Policy (CSP)
- XSS Protection
- HSTS (HTTPS Strict Transport Security)
- Frame Options (Clickjacking protection)

### **Request Logging**
- All authentication attempts
- Failed login tracking
- Security event monitoring
- Geographic anomaly detection

## 📊 **Monitoring & Analytics**

### **Security Dashboard Endpoints**

```
GET /api/v1/auth/security/status/
Authorization: Bearer your_access_token
```

**Response:**
```json
{
    "user_tier": "vip",
    "mfa_enabled": true,
    "mfa_required": true,
    "trusted_devices_count": 2,
    "recent_login_attempts": 5,
    "security_score": "high",
    "recommendations": [
        "Consider adding more trusted devices",
        "Review recent login locations"
    ]
}
```

### **Security Events**

The system tracks various security events:
- Suspicious login attempts
- Multiple failed logins
- Unusual geographic locations
- Rate limit violations
- MFA bypass attempts
- Token manipulation attempts

## 🚨 **Error Handling**

### **Common Error Responses**

**Invalid Credentials:**
```json
{
    "error": "Invalid email or password."
}
```

**MFA Required:**
```json
{
    "mfa_required": true,
    "mfa_methods": ["totp", "sms"],
    "message": "Multi-factor authentication required."
}
```

**Rate Limited:**
```json
{
    "error": "Rate limit exceeded",
    "detail": "Too many requests. Please try again later."
}
```

**Suspicious Activity:**
```json
{
    "error": "Login blocked due to suspicious activity. Please try again later."
}
```

## 🔧 **Development & Testing**

### **Create Test Users**

```python
from accounts.models import User

# Create Normal User
normal_user = User.objects.create_user(
    email='normal@example.com',
    password='testpass123',
    tier='normal'
)

# Create VIP User
vip_user = User.objects.create_user(
    email='vip@example.com',
    password='testpass123',
    tier='vip'
)
```

### **Test MFA Setup**

```python
from accounts.models import MFAToken
import pyotp

# Setup TOTP for user
secret = pyotp.random_base32()
mfa_token = MFAToken.objects.create(
    user=vip_user,
    token_type='totp',
    secret_key=secret,
    is_active=True
)

# Generate test code
totp = pyotp.TOTP(secret)
current_code = totp.now()
print(f"Current TOTP code: {current_code}")
```

## 🚀 **Production Deployment**

### **Security Checklist**

- [ ] Use strong JWT secret key (min 32 characters)
- [ ] Enable HTTPS in production
- [ ] Configure Redis with authentication
- [ ] Set up proper email/SMS services
- [ ] Configure rate limiting
- [ ] Enable security logging
- [ ] Set up monitoring alerts
- [ ] Configure backup procedures

### **Environment Configuration**

```bash
# Production settings
export DJANGO_ENV=production
export JWT_SECRET_KEY=$(openssl rand -base64 32)
export REDIS_URL=redis://username:password@redis-server:6379/1
export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### **Monitoring Setup**

Set up monitoring for:
- Failed login attempts
- Security events
- Rate limit violations
- MFA failures
- Token manipulation attempts

## 📱 **Mobile App Integration**

### **React Native Example**

```javascript
// Authentication service
class AuthService {
    async login(email, password, mfaToken = null) {
        const response = await fetch('/api/v1/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Device-Fingerprint': await this.getDeviceFingerprint()
            },
            body: JSON.stringify({
                email,
                password,
                mfa_token: mfaToken,
                device_fingerprint: await this.getDeviceFingerprint()
            })
        });
        
        return response.json();
    }
    
    async getDeviceFingerprint() {
        // Generate device fingerprint
        const deviceInfo = await DeviceInfo.getDeviceId();
        return deviceInfo;
    }
}
```

## 🔄 **Maintenance**

### **Regular Tasks**

1. **Token Cleanup**: Remove expired tokens
2. **Session Cleanup**: Remove expired sessions
3. **Security Review**: Monitor security events
4. **Device Trust Review**: Review trusted devices
5. **MFA Token Rotation**: Encourage users to refresh TOTP secrets

### **Database Maintenance**

```sql
-- Clean up expired sessions
DELETE FROM user_sessions WHERE expires_at < NOW();

-- Clean up old login attempts (keep 30 days)
DELETE FROM login_attempts WHERE created_at < NOW() - INTERVAL '30 days';

-- Review security events
SELECT event_type, COUNT(*) as count 
FROM security_events 
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY event_type;
```

## 🎯 **Next Steps**

1. **Implement Frontend Integration**: Connect with React Native mobile app
2. **Add Biometric Authentication**: Fingerprint/Face ID support
3. **Enhanced Fraud Detection**: Machine learning-based risk scoring
4. **Admin Dashboard**: Web interface for security monitoring
5. **API Documentation**: Generate Swagger/OpenAPI docs
6. **Load Testing**: Test authentication under high load

## 🆘 **Support**

For issues or questions:
1. Check the error logs in `logs/security.log`
2. Review the security events dashboard
3. Check Redis connectivity
4. Verify email/SMS service configuration
5. Test with development credentials first

---

**Version**: 1.0.0  
**Last Updated**: August 6, 2025  
**Author**: VIP Ride Platform Development Team
