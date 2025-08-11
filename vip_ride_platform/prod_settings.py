"""
Production Settings for VIP Ride-Hailing Platform

This file contains production-specific settings that override
the base settings for deployment.

Usage:
    python manage.py runserver --settings=vip_ride_platform.prod_settings
    gunicorn vip_ride_platform.wsgi:application --env DJANGO_SETTINGS_MODULE=vip_ride_platform.prod_settings
"""

from .settings import *
import dj_database_url

print("🚀 Production settings loaded - Security enabled")

# Production overrides
DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database configuration from environment
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }

# Static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add WhiteNoise middleware for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'vip_ride_platform': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@vipride.com')

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Production-specific settings
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Error reporting
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@vipride.com')),
]
MANAGERS = ADMINS

# Performance optimizations
CONN_MAX_AGE = 600  # Database connection pooling

# Security headers
SECURE_REFERRER_POLICY = 'strict-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Production payment gateway settings
PAYSTACK_TEST_MODE = False
FLUTTERWAVE_TEST_MODE = False
STRIPE_TEST_MODE = False

# Enable strict production mode
STRICT_PRODUCTION_MODE = True

print("🔒 Production security settings applied:")
print(f"   - DEBUG: {DEBUG}")
print(f"   - SECURE_SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
print(f"   - SESSION_COOKIE_SECURE: {SESSION_COOKIE_SECURE}")
print(f"   - CSRF_COOKIE_SECURE: {CSRF_COOKIE_SECURE}")
print(f"   - ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print("🌐 Ready for production deployment!")
