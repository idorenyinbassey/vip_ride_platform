"""
Rate limiting middleware for API endpoints
"""
import time
import threading
from collections import defaultdict
from django.http import JsonResponse
from django.conf import settings


class RateLimitMiddleware:
    """Simple rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # In-memory storage for rate limiting (use Redis in production)
        self.request_counts = defaultdict(list)
        # Thread lock for safe concurrent access
        self.lock = threading.Lock()
        
        # Rate limit configuration
        self.rate_limits = {
            '/api/v1/accounts/register/': {'requests': 5, 'window': 300},  # 5 per 5 minutes
            '/api/v1/accounts/login/': {'requests': 10, 'window': 300},     # 10 per 5 minutes
            '/api/v1/accounts/password/reset/': {'requests': 3, 'window': 600},  # 3 per 10 minutes
        }
        
        # Default rate limit for all API endpoints
        self.default_rate_limit = {'requests': 100, 'window': 3600}  # 100 per hour
    
    def __call__(self, request):
        # Check if this is an API endpoint
        if request.path.startswith('/api/'):
            if not self.check_rate_limit(request):
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'detail': 'Too many requests from this IP address.'
                }, status=429)
        
        response = self.get_response(request)
        return response
    
    def check_rate_limit(self, request):
        """Check if request is within rate limit"""
        ip_address = self.get_client_ip(request)
        path = request.path
        current_time = time.time()
        
        # Get rate limit for this endpoint
        rate_limit = self.rate_limits.get(path, self.default_rate_limit)
        
        # Create key for this IP and endpoint
        key = f"{ip_address}:{path}"
        
        # Thread-safe list mutation
        with self.lock:
            # Clean old requests outside the time window
            self.request_counts[key] = [
                req_time for req_time in self.request_counts[key]
                if current_time - req_time < rate_limit['window']
            ]
            
            # Check if we're over the limit
            if len(self.request_counts[key]) >= rate_limit['requests']:
                return False
            
            # Add current request
            self.request_counts[key].append(current_time)
        
        return True
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
