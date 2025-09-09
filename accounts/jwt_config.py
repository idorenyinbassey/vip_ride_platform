# JWT Authentication Configuration
# Custom JWT settings for VIP ride-hailing platform

from datetime import timedelta
from django.conf import settings

# JWT Token Settings
JWT_AUTH_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'vip-ride-platform',
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    # Token Claims
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': (
        'rest_framework_simplejwt.authentication.'
        'default_user_authentication_rule'
    ),
    
    # Token Response Format
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    # Sliding Tokens (for VIP users)
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# User Tier Configurations
USER_TIER_SETTINGS = {
    'normal': {
        'access_token_lifetime': timedelta(minutes=15),
        'refresh_token_lifetime': timedelta(days=7),
        'rate_limit': {
            'rides_per_hour': 10,
            'api_calls_per_minute': 60,
            'requests_per_hour': 1000,
        },
        'mfa_required': False,
        'mfa_methods': ['email', 'sms'],  # Normal users have basic MFA options if they want it
        'session_timeout': timedelta(hours=2),
    },
    'premium': {
        'access_token_lifetime': timedelta(minutes=20),
        'refresh_token_lifetime': timedelta(days=14),
        'rate_limit': {
            'rides_per_hour': 20,
            'api_calls_per_minute': 120,
            'requests_per_hour': 2000,
        },
        'mfa_required': True,  # Premium users now require MFA
        'mfa_methods': ['email', 'sms', 'totp'],  # Available MFA methods
        'session_timeout': timedelta(hours=4),
    },
        'vip': {
        'access_token_lifetime': timedelta(minutes=30),
        'refresh_token_lifetime': timedelta(days=30),
        'rate_limit': {
            'rides_per_hour': 50,
            'api_calls_per_minute': 300,
            'requests_per_hour': 5000,
        },
        'mfa_required': True,
        'mfa_methods': ['email', 'sms', 'totp', 'biometric'],  # VIP gets all methods including biometric
        'session_timeout': timedelta(hours=8),
        'require_biometric': True,
    }
}

# MFA Settings
MFA_SETTINGS = {
    'providers': {
        'sms': {
            'enabled': True,
            'code_length': 6,
            'code_expiry': timedelta(minutes=5),
            'max_attempts': 3,
        },
        'email': {
            'enabled': True,
            'code_length': 8,
            'code_expiry': timedelta(minutes=10),
            'max_attempts': 3,
        },
        'totp': {
            'enabled': True,
            'issuer': 'VIP Ride Platform',
            'algorithm': 'SHA1',
            'digits': 6,
            'period': 30,
        },
        'biometric': {
            'enabled': True,
            'for_vip_only': True,
            'fallback_to_sms': True,
        }
    },
    'backup_codes': {
        'enabled': True,
        'count': 10,
        'length': 8,
        'single_use': True,
    }
}

# Rate Limiting Settings
RATE_LIMIT_SETTINGS = {
    'enable_rate_limiting': True,
    'rate_limit_header': True,
    'cache_timeout': 300,  # 5 minutes
    'burst_allowance': 1.5,  # 50% burst above normal rate
    'progressive_penalty': True,  # Increase penalties for repeated violations
    'whitelist_ips': [],  # Admin IPs that bypass rate limiting
    'blacklist_threshold': 10,  # Auto-blacklist after X violations
}

# Security Settings
SECURITY_SETTINGS = {
    'max_concurrent_sessions': {
        'normal': 3,
        'premium': 5,
        'vip': 10,
        'concierge': 15,
    },
    'device_tracking': True,
    'location_validation': {
        'vip_only': True,
        'max_distance_km': 1000,  # Alert if login from >1000km away
    },
    'suspicious_activity_detection': True,
    'auto_logout_inactive': {
        'normal': timedelta(hours=1),
        'premium': timedelta(hours=2),
        'vip': timedelta(hours=4),
        'concierge': timedelta(hours=8),
    }
}
