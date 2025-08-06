# Enhanced Authentication Models for JWT and MFA
"""
Additional models for JWT authentication, MFA, and security features
"""

import uuid
import secrets
import pyotp
from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserSession(models.Model):
    """Track user sessions for security and concurrent session management"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Device information
    device_fingerprint = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    
    # Location information
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Session management
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    # Security flags
    is_trusted_device = models.BooleanField(default=False)
    requires_mfa = models.BooleanField(default=False)
    mfa_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_id']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at
    
    def extend_session(self, duration: timedelta = None):
        """Extend session expiration"""
        if duration is None:
            from .jwt_config import USER_TIER_SETTINGS
            tier_config = USER_TIER_SETTINGS.get(
                self.user.tier, 
                USER_TIER_SETTINGS['normal']
            )
            duration = tier_config['session_timeout']
        
        self.expires_at = timezone.now() + duration
        self.save()
    
    def __str__(self):
        return f"Session for {self.user.email} - {self.session_id[:8]}"


class TrustedDevice(models.Model):
    """Manage trusted devices for users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trusted_devices')
    device_fingerprint = models.CharField(max_length=64, db_index=True)
    
    # Device information
    device_name = models.CharField(max_length=100, blank=True)  # User-friendly name
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    
    # Trust settings
    is_active = models.BooleanField(default=True)
    trust_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Trust'),
            ('high', 'High Trust'),
            ('vip', 'VIP Trust'),
        ],
        default='basic'
    )
    
    # Usage tracking
    first_used_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trusted_devices'
        unique_together = ['user', 'device_fingerprint']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_fingerprint']),
            models.Index(fields=['last_used_at']),
        ]
    
    def is_expired(self):
        """Check if device trust is expired"""
        return self.expires_at and timezone.now() > self.expires_at
    
    def increment_usage(self):
        """Increment usage count and update last used"""
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Trusted device for {self.user.email} - {self.device_name or 'Unnamed'}"


class MFAToken(models.Model):
    """Multi-Factor Authentication tokens and settings"""
    
    TOKEN_TYPES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('totp', 'TOTP App'),
        ('backup', 'Backup Code'),
        ('biometric', 'Biometric'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mfa_tokens')
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    
    # Token data (encrypted in production)
    secret_key = models.CharField(max_length=255, blank=True)  # For TOTP
    backup_codes = models.JSONField(default=list, blank=True)  # For backup codes
    phone_number = models.CharField(max_length=20, blank=True)  # For SMS
    email_address = models.EmailField(blank=True)  # For email
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    
    # Usage tracking
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Failure tracking
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mfa_tokens'
        unique_together = ['user', 'token_type']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token_type']),
            models.Index(fields=['is_primary']),
        ]
    
    def generate_totp_secret(self):
        """Generate TOTP secret key"""
        if self.token_type == 'totp':
            self.secret_key = pyotp.random_base32()
            self.save()
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code generation"""
        if self.token_type == 'totp' and self.secret_key:
            return pyotp.totp.TOTP(self.secret_key).provisioning_uri(
                name=self.user.email,
                issuer_name="VIP Ride Platform"
            )
        return None
    
    def verify_totp(self, token: str) -> bool:
        """Verify TOTP token"""
        if self.token_type != 'totp' or not self.secret_key:
            return False
        
        totp = pyotp.TOTP(self.secret_key)
        is_valid = totp.verify(token, valid_window=1)  # Allow 30s window
        
        if is_valid:
            self.last_used_at = timezone.now()
            self.usage_count += 1
            self.failed_attempts = 0
            self.save()
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.locked_until = timezone.now() + timedelta(minutes=15)
            self.save()
        
        return is_valid
    
    def verify_backup_code(self, code: str) -> bool:
        """Verify backup code"""
        if self.token_type != 'backup' or code not in self.backup_codes:
            return False
        
        # Remove used backup code
        self.backup_codes.remove(code)
        self.last_used_at = timezone.now()
        self.usage_count += 1
        self.save()
        
        return True
    
    def generate_backup_codes(self, count: int = 10):
        """Generate new backup codes"""
        if self.token_type == 'backup':
            codes = []
            for _ in range(count):
                code = secrets.token_hex(4).upper()
                codes.append(code)
            self.backup_codes = codes
            self.save()
            return codes
        return []
    
    def is_locked(self) -> bool:
        """Check if MFA token is locked due to failed attempts"""
        return self.locked_until and timezone.now() < self.locked_until
    
    def __str__(self):
        return f"MFA {self.token_type} for {self.user.email}"


class LoginAttempt(models.Model):
    """Track login attempts for security monitoring"""
    
    ATTEMPT_TYPES = [
        ('success', 'Successful Login'),
        ('failed_password', 'Failed Password'),
        ('failed_mfa', 'Failed MFA'),
        ('blocked_suspicious', 'Blocked Suspicious'),
        ('blocked_rate_limit', 'Blocked Rate Limit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_attempts', null=True, blank=True)
    email = models.EmailField()  # Store email even if user doesn't exist
    
    # Attempt details
    attempt_type = models.CharField(max_length=20, choices=ATTEMPT_TYPES)
    success = models.BooleanField(default=False)
    
    # Device and location information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=64, blank=True)
    
    # Location (from IP geolocation)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Additional security info
    is_suspicious = models.BooleanField(default=False)
    risk_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    blocked_reason = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'login_attempts'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['success', 'created_at']),
            models.Index(fields=['is_suspicious']),
        ]
    
    def __str__(self):
        return f"Login attempt by {self.email} - {self.attempt_type}"


class RateLimitTracker(models.Model):
    """Track API rate limits per user and tier"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rate_limits', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    identifier = models.CharField(max_length=100, db_index=True)  # user_id or ip_address
    
    # Rate limit details
    endpoint = models.CharField(max_length=100)
    request_count = models.PositiveIntegerField(default=0)
    window_start = models.DateTimeField()
    window_duration = models.DurationField()  # Window size (e.g., 1 hour)
    
    # Limits (based on user tier)
    limit_per_window = models.PositiveIntegerField()
    burst_allowance = models.PositiveIntegerField(default=0)
    
    # Violation tracking
    violations = models.PositiveIntegerField(default=0)
    last_violation = models.DateTimeField(null=True, blank=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rate_limit_tracker'
        unique_together = ['identifier', 'endpoint']
        indexes = [
            models.Index(fields=['identifier', 'endpoint']),
            models.Index(fields=['window_start']),
            models.Index(fields=['blocked_until']),
        ]
    
    def is_blocked(self) -> bool:
        """Check if currently blocked"""
        return self.blocked_until and timezone.now() < self.blocked_until
    
    def reset_window(self):
        """Reset the rate limit window"""
        self.request_count = 0
        self.window_start = timezone.now()
        self.save()
    
    def increment_request(self) -> bool:
        """Increment request count and check if limit exceeded"""
        # Check if window has expired
        window_end = self.window_start + self.window_duration
        if timezone.now() > window_end:
            self.reset_window()
        
        self.request_count += 1
        
        # Check if limit exceeded
        total_allowed = self.limit_per_window + self.burst_allowance
        if self.request_count > total_allowed:
            self.violations += 1
            self.last_violation = timezone.now()
            
            # Progressive blocking
            if self.violations >= 3:
                self.blocked_until = timezone.now() + timedelta(hours=1)
            elif self.violations >= 5:
                self.blocked_until = timezone.now() + timedelta(hours=24)
        
        self.save()
        return self.request_count <= total_allowed
    
    def __str__(self):
        return f"Rate limit for {self.identifier} - {self.endpoint}"


class SecurityEvent(models.Model):
    """Track security events and incidents"""
    
    EVENT_TYPES = [
        ('suspicious_login', 'Suspicious Login'),
        ('multiple_failed_logins', 'Multiple Failed Logins'),
        ('unusual_location', 'Unusual Location'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('mfa_bypass_attempt', 'MFA Bypass Attempt'),
        ('token_manipulation', 'Token Manipulation'),
        ('concurrent_session_abuse', 'Concurrent Session Abuse'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_events', null=True, blank=True)
    
    # Event details
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    description = models.TextField()
    
    # Context information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Response tracking
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_events')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Automated response
    auto_response_taken = models.CharField(max_length=100, blank=True)
    manual_review_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_events'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['event_type', 'severity']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['created_at']),
        ]
    
    def mark_resolved(self, resolved_by_user, notes: str = ''):
        """Mark security event as resolved"""
        self.is_resolved = True
        self.resolved_by = resolved_by_user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()
    
    def __str__(self):
        return f"Security Event: {self.event_type} - {self.severity}"
