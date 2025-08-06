# GPS Encryption Models
"""
Django models for storing encrypted GPS data and session management
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from rides.models import Ride  # Assuming you have a rides app

User = get_user_model()


class GPSEncryptionSession(models.Model):
    """Model for storing GPS encryption sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=64, unique=True, db_index=True)
    ride = models.OneToOneField(
        Ride, 
        on_delete=models.CASCADE, 
        related_name='encryption_session'
    )
    
    # Session metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used = models.DateTimeField(auto_now=True)
    
    # Encryption statistics
    encryption_count = models.PositiveIntegerField(default=0)
    decryption_count = models.PositiveIntegerField(default=0)
    
    # Session status
    is_active = models.BooleanField(default=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Key exchange metadata (don't store actual keys)
    key_exchange_completed = models.BooleanField(default=False)
    client_public_key_hash = models.CharField(max_length=64, blank=True)
    server_public_key_hash = models.CharField(max_length=64, blank=True)
    
    class Meta:
        db_table = 'gps_encryption_sessions'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['ride', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"GPS Session {self.session_id[:8]} for Ride {self.ride.id}"
    
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at
    
    def end_session(self):
        """End the encryption session"""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()


class EncryptedGPSData(models.Model):
    """Model for storing encrypted GPS coordinates"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        GPSEncryptionSession,
        on_delete=models.CASCADE,
        related_name='gps_data'
    )
    
    # Encrypted data
    encrypted_data = models.TextField()  # Base64 encoded ciphertext
    nonce = models.CharField(max_length=32)  # Base64 encoded nonce
    
    # Metadata
    timestamp = models.DateTimeField()  # GPS timestamp
    recorded_at = models.DateTimeField(auto_now_add=True)  # Server timestamp
    
    # Data source
    source_device = models.CharField(max_length=50, default='mobile_app')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='encrypted_gps_data'
    )
    
    # Additional encrypted fields (optional)
    encrypted_speed = models.TextField(blank=True)
    encrypted_bearing = models.TextField(blank=True)
    encrypted_altitude = models.TextField(blank=True)
    encrypted_accuracy = models.TextField(blank=True)
    
    # Security tracking
    encryption_version = models.CharField(max_length=10, default='1.0')
    checksum = models.CharField(max_length=64, blank=True)
    
    class Meta:
        db_table = 'encrypted_gps_data'
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['user', 'recorded_at']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['recorded_at']),
        ]
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Encrypted GPS data for {self.user.email} at {self.timestamp}"


class GPSDecryptionLog(models.Model):
    """Model for logging GPS decryption attempts"""
    
    DECRYPTION_STATUS = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('unauthorized', 'Unauthorized'),
        ('session_expired', 'Session Expired'),
        ('invalid_data', 'Invalid Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gps_data = models.ForeignKey(
        EncryptedGPSData,
        on_delete=models.CASCADE,
        related_name='decryption_logs'
    )
    
    # Decryption details
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='gps_decryption_requests'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=DECRYPTION_STATUS)
    
    # Request context
    request_reason = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Result metadata
    decryption_time_ms = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'gps_decryption_logs'
        indexes = [
            models.Index(fields=['gps_data', 'requested_at']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['requested_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Decryption {self.status} by {self.requested_by.email}"


class GPSEncryptionAudit(models.Model):
    """Model for auditing GPS encryption system events"""
    
    EVENT_TYPES = [
        ('session_created', 'Session Created'),
        ('session_ended', 'Session Ended'),
        ('session_expired', 'Session Expired'),
        ('encryption_success', 'Encryption Success'),
        ('encryption_failed', 'Encryption Failed'),
        ('decryption_success', 'Decryption Success'),
        ('decryption_failed', 'Decryption Failed'),
        ('key_exchange', 'Key Exchange'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('system_error', 'System Error'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Event details
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    message = models.TextField()
    
    # Context
    session = models.ForeignKey(
        GPSEncryptionSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gps_audit_logs'
    )
    
    # Technical details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gps_encryption_audit'
        indexes = [
            models.Index(fields=['event_type', 'severity']),
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['severity']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.severity} at {self.created_at}"


class GPSSecurityPolicy(models.Model):
    """Model for GPS encryption security policies"""
    
    POLICY_TYPES = [
        ('encryption_required', 'Encryption Required'),
        ('decryption_allowed', 'Decryption Allowed'),
        ('data_retention', 'Data Retention'),
        ('access_control', 'Access Control'),
        ('audit_logging', 'Audit Logging'),
    ]
    
    USER_TIERS = [
        ('normal', 'Normal'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
        ('concierge', 'Concierge'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Policy details
    name = models.CharField(max_length=100)
    policy_type = models.CharField(max_length=30, choices=POLICY_TYPES)
    description = models.TextField()
    
    # Scope
    user_tier = models.CharField(max_length=20, choices=USER_TIERS)
    applies_to_all = models.BooleanField(default=False)
    
    # Policy settings
    is_active = models.BooleanField(default=True)
    enforcement_level = models.CharField(
        max_length=20,
        choices=[
            ('advisory', 'Advisory'),
            ('warning', 'Warning'),
            ('enforced', 'Enforced'),
            ('strict', 'Strict'),
        ],
        default='enforced'
    )
    
    # Configuration
    config = models.JSONField(default=dict)
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_gps_policies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gps_security_policies'
        unique_together = ['policy_type', 'user_tier']
        indexes = [
            models.Index(fields=['policy_type', 'user_tier']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user_tier})"
    
    def get_config_value(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)


class GPSDataRetentionSchedule(models.Model):
    """Model for managing GPS data retention schedules"""
    
    RETENTION_ACTIONS = [
        ('archive', 'Archive'),
        ('delete', 'Delete'),
        ('anonymize', 'Anonymize'),
        ('encrypt_further', 'Additional Encryption'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Retention policy
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Schedule
    retention_days = models.PositiveIntegerField()
    action = models.CharField(max_length=20, choices=RETENTION_ACTIONS)
    
    # Scope
    user_tier = models.CharField(max_length=20, blank=True)
    applies_to_all = models.BooleanField(default=True)
    
    # Execution
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    records_processed = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    
    # Configuration
    config = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gps_data_retention_schedules'
        indexes = [
            models.Index(fields=['is_active', 'next_run']),
            models.Index(fields=['user_tier']),
            models.Index(fields=['last_run']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.retention_days} days"
