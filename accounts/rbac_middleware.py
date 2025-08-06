# RBAC Audit Middleware
"""
Middleware for automatic audit logging of all API requests and permission checks
"""

import logging
import time
import json
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from accounts.models import SecurityEvent

logger = logging.getLogger(__name__)


class RBACauditMiddleware(MiddlewareMixin):
    """Middleware to audit all requests for RBAC compliance"""
    
    # Paths to exclude from audit logging
    EXCLUDED_PATHS = [
        '/admin/jsi18n/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/health/',
        '/ping/',
    ]
    
    # Sensitive data fields to redact in logs
    SENSITIVE_FIELDS = [
        'password',
        'token',
        'secret',
        'key',
        'authorization',
        'cookie',
        'session',
    ]
    
    def process_request(self, request):
        """Process incoming request"""
        # Skip excluded paths
        if self._should_exclude_path(request.path):
            return None
        
        # Add request start time for performance tracking
        request._audit_start_time = time.time()
        
        # Log request details
        self._log_request_start(request)
        
        return None
    
    def process_response(self, request, response):
        """Process outgoing response"""
        # Skip excluded paths
        if self._should_exclude_path(request.path):
            return response
        
        # Calculate request duration
        duration = None
        if hasattr(request, '_audit_start_time'):
            duration = time.time() - request._audit_start_time
        
        # Log response details
        self._log_request_complete(request, response, duration)
        
        return response
    
    def process_exception(self, request, exception):
        """Process exceptions"""
        if self._should_exclude_path(request.path):
            return None
        
        # Log exception details
        self._log_request_exception(request, exception)
        
        return None
    
    def _should_exclude_path(self, path):
        """Check if path should be excluded from auditing"""
        return any(excluded in path for excluded in self.EXCLUDED_PATHS)
    
    def _log_request_start(self, request):
        """Log request start details"""
        try:
            # Extract request data
            request_data = self._extract_request_data(request)
            
            SecurityEvent.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type='request_start',
                event_category='api_audit',
                message=f"Request started: {request.method} {request.path}",
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint=f"{request.method} {request.path}",
                metadata={
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                    'content_type': request.content_type,
                    'user_tier': getattr(request.user, 'tier', None),
                    'authenticated': request.user.is_authenticated if request.user else False,
                    'timestamp': timezone.now().isoformat(),
                    **request_data
                }
            )
        except Exception as e:
            logger.error(f"Failed to log request start: {e}")
    
    def _log_request_complete(self, request, response, duration):
        """Log request completion details"""
        try:
            SecurityEvent.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type='request_complete',
                event_category='api_audit',
                message=f"Request completed: {request.method} {request.path} - {response.status_code}",
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint=f"{request.method} {request.path}",
                metadata={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2) if duration else None,
                    'response_size': len(response.content) if hasattr(response, 'content') else None,
                    'user_tier': getattr(request.user, 'tier', None),
                    'authenticated': request.user.is_authenticated if request.user else False,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to log request completion: {e}")
    
    def _log_request_exception(self, request, exception):
        """Log request exceptions"""
        try:
            SecurityEvent.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type='request_exception',
                event_category='api_error',
                message=f"Request exception: {request.method} {request.path} - {str(exception)}",
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint=f"{request.method} {request.path}",
                metadata={
                    'method': request.method,
                    'path': request.path,
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception),
                    'user_tier': getattr(request.user, 'tier', None),
                    'authenticated': request.user.is_authenticated if request.user else False,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to log request exception: {e}")
    
    def _extract_request_data(self, request):
        """Extract and sanitize request data"""
        data = {}
        
        try:
            # Extract POST data (sanitized)
            if request.method in ['POST', 'PUT', 'PATCH'] and request.content_type:
                if 'application/json' in request.content_type:
                    try:
                        body_data = json.loads(request.body.decode('utf-8'))
                        data['body_fields'] = list(body_data.keys())
                        data['body_size'] = len(request.body)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        data['body_size'] = len(request.body)
                elif 'application/x-www-form-urlencoded' in request.content_type:
                    data['form_fields'] = list(request.POST.keys())
            
            # Extract headers (sanitized)
            headers = {}
            for key, value in request.META.items():
                if key.startswith('HTTP_'):
                    header_name = key[5:].lower()
                    if not any(sensitive in header_name for sensitive in self.SENSITIVE_FIELDS):
                        headers[header_name] = value[:100]  # Truncate long headers
            
            data['headers'] = headers
            
        except Exception as e:
            logger.warning(f"Failed to extract request data: {e}")
        
        return data
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityMonitoringMiddleware(MiddlewareMixin):
    """Middleware for detecting suspicious activity"""
    
    # Thresholds for suspicious activity
    RATE_LIMIT_THRESHOLDS = {
        'requests_per_minute': 100,
        'failed_auth_per_hour': 10,
        'permission_denied_per_hour': 20
    }
    
    def process_response(self, request, response):
        """Monitor response for suspicious patterns"""
        # Check for authentication failures
        if response.status_code == 401:
            self._check_auth_failures(request)
        
        # Check for permission denials
        elif response.status_code == 403:
            self._check_permission_denials(request)
        
        # Check for rate limiting violations
        self._check_rate_limits(request)
        
        return response
    
    def _check_auth_failures(self, request):
        """Check for excessive authentication failures"""
        try:
            ip_address = self._get_client_ip(request)
            
            # Count recent auth failures from this IP
            recent_failures = SecurityEvent.objects.filter(
                ip_address=ip_address,
                event_type='authentication_failed',
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            if recent_failures >= self.RATE_LIMIT_THRESHOLDS['failed_auth_per_hour']:
                SecurityEvent.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    event_type='suspicious_activity',
                    event_category='security_alert',
                    message=f"Excessive authentication failures from IP: {ip_address}",
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    endpoint=f"{request.method} {request.path}",
                    metadata={
                        'alert_type': 'excessive_auth_failures',
                        'failure_count': recent_failures,
                        'threshold': self.RATE_LIMIT_THRESHOLDS['failed_auth_per_hour'],
                        'timestamp': timezone.now().isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Failed to check auth failures: {e}")
    
    def _check_permission_denials(self, request):
        """Check for excessive permission denials"""
        try:
            ip_address = self._get_client_ip(request)
            
            # Count recent permission denials from this IP
            recent_denials = SecurityEvent.objects.filter(
                ip_address=ip_address,
                event_type='access_denied',
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            if recent_denials >= self.RATE_LIMIT_THRESHOLDS['permission_denied_per_hour']:
                SecurityEvent.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    event_type='suspicious_activity',
                    event_category='security_alert',
                    message=f"Excessive permission denials from IP: {ip_address}",
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    endpoint=f"{request.method} {request.path}",
                    metadata={
                        'alert_type': 'excessive_permission_denials',
                        'denial_count': recent_denials,
                        'threshold': self.RATE_LIMIT_THRESHOLDS['permission_denied_per_hour'],
                        'timestamp': timezone.now().isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Failed to check permission denials: {e}")
    
    def _check_rate_limits(self, request):
        """Check for rate limiting violations"""
        try:
            ip_address = self._get_client_ip(request)
            
            # Count requests from this IP in the last minute
            recent_requests = SecurityEvent.objects.filter(
                ip_address=ip_address,
                event_type='request_start',
                created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
            ).count()
            
            if recent_requests >= self.RATE_LIMIT_THRESHOLDS['requests_per_minute']:
                SecurityEvent.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    event_type='suspicious_activity',
                    event_category='security_alert',
                    message=f"Rate limit exceeded from IP: {ip_address}",
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    endpoint=f"{request.method} {request.path}",
                    metadata={
                        'alert_type': 'rate_limit_exceeded',
                        'request_count': recent_requests,
                        'threshold': self.RATE_LIMIT_THRESHOLDS['requests_per_minute'],
                        'timestamp': timezone.now().isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Failed to check rate limits: {e}")
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
