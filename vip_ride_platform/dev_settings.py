"""
Development-specific Django settings
Import this in development to override production security settings

Usage:
    python manage.py runserver --settings=vip_ride_platform.dev_settings
"""
from .settings import *

# Override for development
DEBUG = True

# Disable SSL redirects for development server
SECURE_SSL_REDIRECT = False

# Disable secure cookies for development (HTTP)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable HSTS for development
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Allow all hosts for development
ALLOWED_HOSTS = ['*']

# Disable strict production mode
STRICT_PRODUCTION_MODE = False

# Development-friendly CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Development logging - more verbose
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development secret key (less secure, for development only)
SECRET_KEY = 'dev-key-not-for-production-use-only-for-local-development-123456'

# Development-specific settings
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Auth redirects for development: use marketing login and portal home
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/portal/'
LOGOUT_REDIRECT_URL = '/login/'

# Development payment gateways (all in test mode)
PAYSTACK_TEST_MODE = True
FLUTTERWAVE_TEST_MODE = True
STRIPE_TEST_MODE = True

print("🚀 Development settings loaded - SSL redirects disabled for local development")
print("🔧 Development overrides applied:")
print(f"   - DEBUG: {DEBUG}")
print(f"   - SECURE_SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
print(f"   - SESSION_COOKIE_SECURE: {SESSION_COOKIE_SECURE}")
print(f"   - CSRF_COOKIE_SECURE: {CSRF_COOKIE_SECURE}")
print("📝 Ready for development on HTTP!")
