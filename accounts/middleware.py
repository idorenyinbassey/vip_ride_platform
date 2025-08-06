# Rate Limiting Middleware
"""
Middleware for implementing tier-based rate limiting
"""

import time
from collections import defaultdict
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from .jwt_config import RATE_LIMIT_SETTINGS
from .utils import get_client_ip


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware for tier-based rate limiting"""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.rate_limits = RATE_LIMIT_SETTINGS
        
    def process_request(self, request):
        """Check rate limits before processing request"""
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit(request):
            return None
        
        # Get identifier (user ID or IP)
        identifier = self._get_identifier(request)
        
        # Get rate limit for user tier
        rate_limit = self._get_rate_limit(request)
        
        # Check if rate limit exceeded
        if self._is_rate_limited(identifier, rate_limit):
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'detail': 'Too many requests. Please try again later.'
                },
                status=429
            )
        
        return None
    
    def _should_skip_rate_limit(self, request):
        """Check if rate limiting should be skipped"""
        skip_paths = [
            '/admin/',
            '/health/',
            '/metrics/',
        ]
        
        for path in skip_paths:
            if request.path.startswith(path):
                return True
        
        return False
    
    def _get_identifier(self, request):
        """Get unique identifier for rate limiting"""
        if request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            ip_address = get_client_ip(request)
            return f"ip:{ip_address}"
    
    def _get_rate_limit(self, request):
        """Get rate limit based on user tier"""
        if request.user.is_authenticated:
            tier = getattr(request.user, 'tier', 'normal')
            return self.rate_limits.get(tier, self.rate_limits['normal'])
        else:
            return self.rate_limits['anonymous']
    
    def _is_rate_limited(self, identifier, rate_limit):
        """Check if identifier has exceeded rate limit"""
        now = time.time()
        window_duration = rate_limit['window']
        max_requests = rate_limit['requests']
        
        # Get current window start
        window_start = now - (now % window_duration)
        cache_key = f"rate_limit:{identifier}:{window_start}"
        
        # Get current request count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= max_requests:
            return True
        
        # Increment counter
        cache.set(cache_key, current_count + 1, timeout=window_duration)
        
        return False


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware for adding security headers"""
    
    def process_response(self, request, response):
        """Add security headers to response"""
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none';"
        )
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(self), '
            'camera=(), '
            'microphone=(), '
            'payment=(self)'
        )
        
        # HSTS (only in production with HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging requests for security monitoring"""
    
    def process_request(self, request):
        """Log request details"""
        # Store request start time
        request._start_time = time.time()
        
        # Log sensitive endpoints
        if self._is_sensitive_endpoint(request):
            self._log_request(request)
        
        return None
    
    def process_response(self, request, response):
        """Log response details"""
        # Calculate request duration
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        # Log failed attempts
        if response.status_code in [400, 401, 403, 429]:
            self._log_failed_request(request, response)
        
        return response
    
    def _is_sensitive_endpoint(self, request):
        """Check if endpoint is sensitive and needs logging"""
        sensitive_paths = [
            '/api/auth/login/',
            '/api/auth/logout/',
            '/api/auth/register/',
            '/api/auth/mfa/',
            '/api/auth/password/',
        ]
        
        for path in sensitive_paths:
            if request.path.startswith(path):
                return True
        
        return False
    
    def _log_request(self, request):
        """Log request details"""
        import logging
        logger = logging.getLogger('security')
        
        log_data = {
            'path': request.path,
            'method': request.method,
            'ip': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user': str(request.user) if request.user.is_authenticated else 'anonymous'
        }
        
        logger.info(f"Request: {log_data}")
    
    def _log_failed_request(self, request, response):
        """Log failed request details"""
        import logging
        logger = logging.getLogger('security')
        
        log_data = {
            'path': request.path,
            'method': request.method,
            'status': response.status_code,
            'ip': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user': str(request.user) if request.user.is_authenticated else 'anonymous'
        }
        
        logger.warning(f"Failed request: {log_data}")


class GeoLocationMiddleware(MiddlewareMixin):
    """Middleware for geolocation-based access control"""
    
    def process_request(self, request):
        """Check geolocation restrictions"""
        # Skip for non-authenticated users or certain paths
        if not request.user.is_authenticated or self._should_skip_geo_check(request):
            return None
        
        # Get user's location
        user_location = self._get_user_location(request)
        
        # Check VIP users for geo restrictions
        if request.user.tier == 'vip':
            allowed_countries = self._get_allowed_countries(request.user)
            
            if user_location and user_location.get('country') not in allowed_countries:
                return JsonResponse(
                    {
                        'error': 'Access denied',
                        'detail': 'Access not allowed from this location.'
                    },
                    status=403
                )
        
        return None
    
    def _should_skip_geo_check(self, request):
        """Check if geolocation check should be skipped"""
        skip_paths = [
            '/api/auth/logout/',
            '/api/auth/security/',
        ]
        
        for path in skip_paths:
            if request.path.startswith(path):
                return True
        
        return False
    
    def _get_user_location(self, request):
        """Get user's location from IP"""
        # This would use a geolocation service
        # For now, return None to skip geo checks
        return None
    
    def _get_allowed_countries(self, user):
        """Get allowed countries for user"""
        # This would query user settings or tier defaults
        return ['NG', 'GH', 'KE']  # Nigeria, Ghana, Kenya
