# GPS Encryption API Serializers
"""
Serializers for GPS encryption API endpoints
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from core.gps_models import (
    GPSEncryptionSession,
    EncryptedGPSData,
    GPSDecryptionLog,
    GPSEncryptionAudit
)


class KeyExchangeRequestSerializer(serializers.Serializer):
    """Serializer for ECDH key exchange request"""
    
    client_public_key = serializers.CharField(
        max_length=200,
        help_text="Base64 encoded client public key"
    )
    ride_id = serializers.UUIDField(
        help_text="Ride ID for encryption session"
    )
    
    def validate_client_public_key(self, value):
        """Validate client public key format"""
        import base64
        try:
            decoded = base64.b64decode(value)
            if len(decoded) < 32:  # Minimum key size
                raise serializers.ValidationError("Invalid public key size")
        except Exception:
            raise serializers.ValidationError("Invalid public key format")
        return value


class KeyExchangeResponseSerializer(serializers.Serializer):
    """Serializer for ECDH key exchange response"""
    
    session_id = serializers.CharField()
    server_public_key = serializers.CharField()
    expires_at = serializers.DateTimeField()
    session_timeout = serializers.IntegerField()


class GPSEncryptionRequestSerializer(serializers.Serializer):
    """Serializer for GPS encryption request"""
    
    session_id = serializers.CharField(
        max_length=64,
        help_text="Encryption session ID"
    )
    latitude = serializers.FloatField(
        min_value=-90.0,
        max_value=90.0,
        help_text="GPS latitude"
    )
    longitude = serializers.FloatField(
        min_value=-180.0,
        max_value=180.0,
        help_text="GPS longitude"
    )
    timestamp = serializers.DateTimeField(
        help_text="GPS timestamp"
    )
    
    # Optional fields
    speed = serializers.FloatField(required=False, min_value=0.0)
    bearing = serializers.FloatField(required=False, min_value=0.0, max_value=360.0)
    altitude = serializers.FloatField(required=False)
    accuracy = serializers.FloatField(required=False, min_value=0.0)
    
    def validate_timestamp(self, value):
        """Validate GPS timestamp is reasonable"""
        now = timezone.now()
        if value > now + timedelta(minutes=5):
            raise serializers.ValidationError("Timestamp cannot be in the future")
        if value < now - timedelta(hours=24):
            raise serializers.ValidationError("Timestamp is too old")
        return value


class GPSEncryptionResponseSerializer(serializers.Serializer):
    """Serializer for GPS encryption response"""
    
    success = serializers.BooleanField()
    data_id = serializers.UUIDField(allow_null=True)
    encrypted_at = serializers.DateTimeField()
    message = serializers.CharField(required=False)


class GPSDecryptionRequestSerializer(serializers.Serializer):
    """Serializer for GPS decryption request"""
    
    data_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100,
        help_text="List of encrypted GPS data IDs to decrypt"
    )
    reason = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Reason for decryption request"
    )


class DecryptedGPSDataSerializer(serializers.Serializer):
    """Serializer for decrypted GPS data"""
    
    data_id = serializers.UUIDField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    speed = serializers.FloatField(allow_null=True)
    bearing = serializers.FloatField(allow_null=True)
    altitude = serializers.FloatField(allow_null=True)
    accuracy = serializers.FloatField(allow_null=True)
    
    # Metadata
    user_email = serializers.EmailField()
    recorded_at = serializers.DateTimeField()
    source_device = serializers.CharField()


class GPSDecryptionResponseSerializer(serializers.Serializer):
    """Serializer for GPS decryption response"""
    
    success = serializers.BooleanField()
    decrypted_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    data = DecryptedGPSDataSerializer(many=True)
    errors = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class GPSEncryptionSessionSerializer(serializers.ModelSerializer):
    """Serializer for GPS encryption session"""
    
    is_expired = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    data_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GPSEncryptionSession
        fields = [
            'id', 'session_id', 'ride_id', 'created_at', 'expires_at',
            'last_used', 'encryption_count', 'decryption_count',
            'is_active', 'ended_at', 'key_exchange_completed',
            'is_expired', 'duration_minutes', 'data_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']
    
    def get_is_expired(self, obj):
        """Check if session is expired"""
        return obj.is_expired()
    
    def get_duration_minutes(self, obj):
        """Calculate session duration in minutes"""
        if obj.ended_at:
            duration = obj.ended_at - obj.created_at
        else:
            duration = timezone.now() - obj.created_at
        return int(duration.total_seconds() / 60)
    
    def get_data_count(self, obj):
        """Get count of encrypted GPS data points"""
        return obj.gps_data.count()


class EncryptedGPSDataSerializer(serializers.ModelSerializer):
    """Serializer for encrypted GPS data"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    session_id = serializers.CharField(source='session.session_id', read_only=True)
    decryption_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EncryptedGPSData
        fields = [
            'id', 'session_id', 'encrypted_data', 'nonce', 'timestamp',
            'recorded_at', 'source_device', 'user_email', 'encryption_version',
            'checksum', 'decryption_count'
        ]
        read_only_fields = [
            'id', 'recorded_at', 'user_email', 'session_id', 'decryption_count'
        ]
    
    def get_decryption_count(self, obj):
        """Get count of decryption attempts"""
        return obj.decryption_logs.count()


class GPSDecryptionLogSerializer(serializers.ModelSerializer):
    """Serializer for GPS decryption logs"""
    
    requested_by_email = serializers.EmailField(
        source='requested_by.email',
        read_only=True
    )
    data_timestamp = serializers.DateTimeField(
        source='gps_data.timestamp',
        read_only=True
    )
    
    class Meta:
        model = GPSDecryptionLog
        fields = [
            'id', 'requested_by_email', 'requested_at', 'status',
            'request_reason', 'ip_address', 'decryption_time_ms',
            'error_message', 'data_timestamp'
        ]
        read_only_fields = ['id', 'requested_at']


class GPSEncryptionAuditSerializer(serializers.ModelSerializer):
    """Serializer for GPS encryption audit logs"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    session_id = serializers.CharField(
        source='session.session_id',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = GPSEncryptionAudit
        fields = [
            'id', 'event_type', 'severity', 'message', 'session_id',
            'user_email', 'ip_address', 'user_agent', 'request_id',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SessionStatusSerializer(serializers.Serializer):
    """Serializer for session status response"""
    
    session_id = serializers.CharField()
    is_active = serializers.BooleanField()
    is_expired = serializers.BooleanField()
    expires_at = serializers.DateTimeField()
    time_remaining_seconds = serializers.IntegerField()
    encryption_count = serializers.IntegerField()
    last_activity = serializers.DateTimeField()


class SessionTerminationSerializer(serializers.Serializer):
    """Serializer for session termination request"""
    
    session_id = serializers.CharField(max_length=64)
    reason = serializers.CharField(
        max_length=100,
        required=False,
        default="Manual termination"
    )


class SessionTerminationResponseSerializer(serializers.Serializer):
    """Serializer for session termination response"""
    
    success = serializers.BooleanField()
    session_id = serializers.CharField()
    ended_at = serializers.DateTimeField()
    final_stats = serializers.DictField()
    message = serializers.CharField()


class GPSEncryptionStatsSerializer(serializers.Serializer):
    """Serializer for GPS encryption statistics"""
    
    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    expired_sessions = serializers.IntegerField()
    total_encryptions = serializers.IntegerField()
    total_decryptions = serializers.IntegerField()
    data_points_today = serializers.IntegerField()
    avg_session_duration_minutes = serializers.FloatField()
    encryption_success_rate = serializers.FloatField()
    
    # Per-tier statistics
    tier_stats = serializers.DictField()
    
    # Recent activity
    recent_sessions = GPSEncryptionSessionSerializer(many=True)
    recent_audit_events = GPSEncryptionAuditSerializer(many=True)


class BulkDecryptionRequestSerializer(serializers.Serializer):
    """Serializer for bulk GPS data decryption"""
    
    FILTER_CHOICES = [
        ('time_range', 'Time Range'),
        ('ride_id', 'Ride ID'),
        ('user_id', 'User ID'),
        ('session_id', 'Session ID'),
    ]
    
    filter_type = serializers.ChoiceField(choices=FILTER_CHOICES)
    filter_value = serializers.CharField(max_length=200)
    
    # Optional time range
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    
    # Processing options
    max_records = serializers.IntegerField(
        default=1000,
        min_value=1,
        max_value=10000
    )
    include_metadata = serializers.BooleanField(default=True)
    reason = serializers.CharField(max_length=200)
    
    def validate(self, data):
        """Validate bulk decryption request"""
        if data['filter_type'] == 'time_range':
            if not data.get('start_time') or not data.get('end_time'):
                raise serializers.ValidationError(
                    "start_time and end_time required for time_range filter"
                )
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "start_time must be before end_time"
                )
        
        return data


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    
    error = serializers.CharField()
    error_code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()
    request_id = serializers.CharField(required=False)
