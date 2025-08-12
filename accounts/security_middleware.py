"""
Security middleware to block access to sensitive endpoints and add security headers
"""
from django.http import HttpResponseNotFound, HttpResponse
from django.conf import settings


class CustomSecurityMiddleware:
    """Custom security middleware for additional protection"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define blocked paths
        self.blocked_paths = [
            '/api/v1/debug/',
            '/debug/',
            '/.env',
            '/config/',
            '/api/v1/health/detailed/',
        ]
        
        # Admin paths that should be restricted
        self.admin_paths = [
            '/api/v1/admin/',
        ]
    
    def __call__(self, request):
        # Block access to sensitive debug endpoints
        for blocked_path in self.blocked_paths:
            if request.path.startswith(blocked_path):
                return HttpResponseNotFound()
        
        # Restrict admin paths to staff only
        for admin_path in self.admin_paths:
            if request.path.startswith(admin_path):
                if not (request.user.is_authenticated and request.user.is_staff):
                    return HttpResponseNotFound()
        
        response = self.get_response(request)
        
        # Add security headers
        self.add_security_headers(response)
        
        return response
    
    def add_security_headers(self, response):
        """Add security headers to all responses"""
        
        # Prevent clickjacking
        if not response.get('X-Frame-Options'):
            response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        if not response.get('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        if not response.get('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'
        
        # HSTS (only in production with HTTPS)
        if settings.SECURE_SSL_REDIRECT and not response.get('Strict-Transport-Security'):
            response['Strict-Transport-Security'] = f'max-age={settings.SECURE_HSTS_SECONDS}; includeSubDomains'
            if settings.SECURE_HSTS_PRELOAD:
                response['Strict-Transport-Security'] += '; preload'
        
        # Content Security Policy (basic)
        if not response.get('Content-Security-Policy'):
            # Allow Tailwind CDN and HTMX (unpkg) so marketing site assets load
            csp_directives = [
                "default-src 'self'",
                (
                    "script-src 'self' 'unsafe-inline' "
                    "https://cdn.tailwindcss.com https://unpkg.com"
                ),
                "style-src 'self' 'unsafe-inline' https:",
                "img-src 'self' data: https:",
                "font-src 'self' https:",
                "connect-src 'self'",
                "frame-ancestors 'none'"
            ]
            response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Referrer Policy
        if not response.get('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy / Permissions Policy
        if not response.get('Permissions-Policy'):
            permissions = [
                'camera=()',
                'microphone=()',
                'geolocation=(self)',
                'payment=(self)'
            ]
            response['Permissions-Policy'] = ', '.join(permissions)
        
        return response
