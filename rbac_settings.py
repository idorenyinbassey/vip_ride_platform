# RBAC Django Settings Configuration
"""
Settings configuration for role-based access control system
Add this to your Django settings.py file
"""

# =====================================
# RBAC MIDDLEWARE CONFIGURATION
# =====================================

# Add RBAC middleware to your middleware stack
# This should be added after authentication middleware
RBAC_MIDDLEWARE = [
    'accounts.rbac_middleware.RBACauditMiddleware',
    'accounts.rbac_middleware.SecurityMonitoringMiddleware',
]

# =====================================
# RBAC AUTHENTICATION SETTINGS
# =====================================

# Enhanced authentication configuration for RBAC
AUTH_USER_MODEL = 'accounts.User'

# JWT settings for API authentication
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key-here',  # Use environment variable
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# =====================================
# RBAC PERMISSION SETTINGS
# =====================================

# Default permission classes for DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'accounts.permissions.AuditedTierPermission',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# =====================================
# RBAC SECURITY SETTINGS
# =====================================

# Session security settings
SESSION_COOKIE_SECURE = True  # Enable in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 hour

# CSRF protection
CSRF_COOKIE_SECURE = True  # Enable in production with HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# =====================================
# RBAC AUDIT SETTINGS
# =====================================

# Audit logging configuration
RBAC_AUDIT_SETTINGS = {
    'ENABLE_AUDIT_LOGGING': True,
    'LOG_SUCCESSFUL_REQUESTS': True,
    'LOG_FAILED_REQUESTS': True,
    'LOG_PERMISSION_CHECKS': True,
    'LOG_MFA_EVENTS': True,
    'LOG_VIP_DATA_ACCESS': True,
    'SANITIZE_REQUEST_DATA': True,
    'MAX_REQUEST_BODY_SIZE': 1024 * 10,  # 10KB max for audit logs
    'AUDIT_RETENTION_DAYS': 90,
    'ENABLE_REAL_TIME_ALERTS': True,
}

# Security monitoring settings
RBAC_SECURITY_SETTINGS = {
    'ENABLE_SUSPICIOUS_ACTIVITY_DETECTION': True,
    'MAX_FAILED_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 300,  # 5 minutes
    'RATE_LIMIT_THRESHOLD': 100,  # requests per minute
    'ENABLE_IP_BLOCKING': True,
    'SUSPICIOUS_USER_AGENTS': [
        'curl',
        'wget',
        'python-requests',
        'bot',
        'crawler',
        'spider',
    ],
    'MONITOR_VIP_REQUESTS': True,
    'ALERT_ON_PRIVILEGE_ESCALATION': True,
}

# =====================================
# RBAC MFA SETTINGS
# =====================================

# Multi-factor authentication settings
RBAC_MFA_SETTINGS = {
    'ENABLE_MFA': True,
    'MFA_REQUIRED_FOR_TIERS': ['vip', 'concierge', 'admin'],
    'MFA_REQUIRED_FOR_OPERATIONS': [
        'sensitive_data_access',
        'financial_operations',
        'user_management',
        'system_configuration',
    ],
    'TOTP_ISSUER_NAME': 'VIP Ride-Hailing Platform',
    'TOTP_VALIDITY_PERIOD': 300,  # 5 minutes
    'BACKUP_CODES_COUNT': 10,
    'FORCE_MFA_SETUP_ON_FIRST_LOGIN': True,
}

# =====================================
# RBAC TIER SETTINGS
# =====================================

# User tier configuration
RBAC_TIER_SETTINGS = {
    'TIER_HIERARCHY': [
        'normal',    # Level 1
        'premium',   # Level 2
        'vip',       # Level 3
        'concierge', # Level 4
        'admin',     # Level 5
    ],
    'TIER_PERMISSIONS': {
        'normal': [
            'ride_request',
            'ride_history',
            'profile_view',
            'payment_methods',
        ],
        'premium': [
            'luxury_vehicles',
            'hotel_booking',
            'priority_support',
            'ride_scheduling',
        ],
        'vip': [
            'encrypted_gps',
            'sos_emergency',
            'trusted_drivers',
            'concierge_service',
        ],
        'concierge': [
            'vip_data_access',
            'emergency_response',
            'driver_management',
            'fleet_oversight',
        ],
        'admin': [
            'system_configuration',
            'user_management',
            'financial_operations',
            'audit_access',
        ],
    },
}

# =====================================
# RBAC LOGGING CONFIGURATION
# =====================================

# Enhanced logging for RBAC
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'rbac_audit': {
            'format': '[RBAC-AUDIT] {asctime} {levelname} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'django.log'),
            'formatter': 'verbose',
        },
        'rbac_audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'rbac_audit.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'rbac_audit',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('logs', 'security.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'rbac_audit': {
            'handlers': ['rbac_audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =====================================
# EXAMPLE COMPLETE MIDDLEWARE STACK
# =====================================

# Complete middleware configuration with RBAC
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # RBAC Middleware (add after authentication)
    'accounts.rbac_middleware.RBACauditMiddleware',
    'accounts.rbac_middleware.SecurityMonitoringMiddleware',
]

# =====================================
# PRODUCTION SECURITY SETTINGS
# =====================================

# Additional security settings for production
if not DEBUG:
    # Force HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Additional headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Session security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # RBAC specific production settings
    RBAC_AUDIT_SETTINGS['ENABLE_REAL_TIME_ALERTS'] = True
    RBAC_SECURITY_SETTINGS['ENABLE_IP_BLOCKING'] = True

# =====================================
# MANAGEMENT COMMANDS FOR RBAC SETUP
# =====================================

# After adding these settings, run these commands:
"""
# 1. Create RBAC permissions and groups
python manage.py setup_rbac

# 2. Test RBAC system
python manage.py test_rbac --test-type=all --create-test-users --verbose

# 3. Create superuser with admin tier
python manage.py createsuperuser

# 4. Migrate database
python manage.py makemigrations
python manage.py migrate

# 5. Create logs directory
mkdir logs

# 6. Test API endpoints with different user tiers
"""
