# Security Testing Scripts Usage Guide

## Overview
This directory contains two comprehensive security testing scripts for the VIP ride-hailing platform:

1. **security_vulnerability_test.py** - Runtime security vulnerability scanner
2. **django_security_checker.py** - Static configuration security checker

## 🛡️ Security Vulnerability Test (Runtime)

### What it tests:
- **Authentication & Authorization**: Bypass attempts, invalid tokens
- **Injection Attacks**: SQL injection, XSS, command injection
- **Rate Limiting**: DoS protection, brute force protection
- **Information Disclosure**: Debug info leaks, error message exposure
- **CORS & Headers**: Security headers, cross-origin policies
- **API Endpoint Security**: HTTP method security, parameter pollution
- **VIP-Specific Security**: GPS encryption, control center access, payment security

### Usage:
```bash
# Make sure Django server is running first
python manage.py runserver

# In another terminal, run the security test
python security_vulnerability_test.py
```

### Sample Output:
```
🛡️  VIP Ride-Hailing Platform Security Vulnerability Scanner
======================================================================
⚠️  WARNING: Only use this tool on applications you own!
======================================================================

🔐 Testing Authentication & Authorization
==================================================
✅ [2025-08-09 15:30:15] Auth Bypass Check: Protected endpoint /api/v1/accounts/profile/ properly secured
❌ [2025-08-09 15:30:16] Auth Bypass Check: Protected endpoint /api/v1/rides/request/ accessible without authentication
...

🛡️  SECURITY VULNERABILITY ASSESSMENT REPORT
============================================================
📊 TEST SUMMARY:
✅ Tests Passed: 45
❌ Tests Failed: 3
⚠️  Warnings: 8
🚨 Vulnerabilities Found: 3

🏆 SECURITY SCORE: 78.2/100
🟡 Good security with minor issues
```

## 🔒 Django Security Checker (Static)

### What it checks:
- **Django Settings**: DEBUG, SECRET_KEY, ALLOWED_HOSTS
- **Database Security**: Hardcoded credentials, database type
- **Security Middleware**: Required middleware components
- **HTTPS Settings**: SSL/TLS configuration
- **Session Security**: Cookie security settings
- **Password Validation**: Password strength requirements
- **CORS Configuration**: Cross-origin resource sharing
- **File Permissions**: Sensitive file access controls
- **Environment Variables**: .env file usage

### Usage:
```bash
# Run from project directory
python django_security_checker.py

# Or specify project path
python django_security_checker.py /path/to/django/project
```

### Sample Output:
```
🔒 Django Security Configuration Checker
==================================================
📁 Checking: /path/to/vip_ride_platform/settings.py

📊 SECURITY CONFIGURATION REPORT
==================================================

🚨 CRITICAL ISSUES:
  ❌ DEBUG = True in production
     Debug mode should be disabled in production
     → Set DEBUG = False

🔴 HIGH PRIORITY ISSUES:
  ❌ CORS allows all origins
     CORS_ALLOW_ALL_ORIGINS = True is insecure
     → Use CORS_ALLOWED_ORIGINS with specific domains

⚠️  WARNINGS:
  ⚠️  Missing SECURE_SSL_REDIRECT
     HTTPS security setting missing: Force HTTPS redirects
     → Add SECURE_SSL_REDIRECT = True for production

✅ PASSED CHECKS:
  ✅ SECRET_KEY loaded from environment variable
  ✅ ALLOWED_HOSTS properly configured
  ✅ Password validation properly configured

📈 SUMMARY:
  Critical Issues: 1
  High Issues: 1
  Warnings: 12
  Passed: 15
  Total Issues: 14
  Security Score: 51.7/100
```

## 🚨 Security Severity Levels

### Critical
- Immediate security risks that could lead to system compromise
- Examples: Exposed admin panels, authentication bypass, hardcoded secrets

### High
- Significant security vulnerabilities requiring prompt attention
- Examples: CORS misconfigurations, missing authentication

### Medium
- Security issues that should be addressed during next maintenance
- Examples: Information disclosure, weak session management

### Warning
- Security best practices and recommendations
- Examples: Missing security headers, suboptimal configurations

## 🛠️ How to Fix Common Issues

### 1. Authentication Issues
```python
# Ensure all protected views require authentication
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
```

### 2. Rate Limiting
```python
# Add to settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### 3. Security Headers
```python
# Add to settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 4. Input Validation
```python
# Use Django REST Framework serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        # Custom validation logic
        return value
```

## 📅 Recommended Testing Schedule

### Development
- Run both scripts before each commit
- Integrate into CI/CD pipeline

### Staging
- Weekly automated security scans
- Manual penetration testing monthly

### Production
- Daily automated security checks
- Quarterly professional security audits

## ⚠️ Important Notes

1. **Only test your own applications** - These tools should only be used on systems you own or have explicit permission to test.

2. **Test in safe environments** - Run comprehensive tests in staging/development environments first.

3. **Monitor server resources** - Security tests can be resource-intensive, especially rate limiting tests.

4. **Regular updates** - Keep security testing scripts updated as the application evolves.

5. **False positives** - Review all findings manually as automated tools may generate false positives.

## 🔗 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django REST Framework Security](https://www.django-rest-framework.org/topics/security/)
- [Web Application Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## 📞 Support

For questions about these security testing scripts or security findings:
1. Review the Django security documentation
2. Check OWASP guidelines for the specific vulnerability type
3. Consider consulting with a security professional for critical issues
