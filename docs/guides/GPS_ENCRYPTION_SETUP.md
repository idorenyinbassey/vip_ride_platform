# GPS Encryption System - Installation & Setup Guide

## Overview

This GPS encryption system provides enterprise-grade AES-256-GCM encryption for GPS coordinates with ECDH key exchange, designed specifically for the VIP ride-hailing platform.

## Features

- **AES-256-GCM Encryption**: Industry-standard encryption for GPS coordinates
- **ECDH Key Exchange**: Secure key derivation using SECP256R1 curve
- **Per-Ride Sessions**: Individual encryption sessions for each ride
- **Background Processing**: Non-blocking encryption operations
- **Session Management**: Automatic session expiry and cleanup
- **Comprehensive Auditing**: Full security event logging
- **Tier-Based Access**: Different access levels for user tiers
- **Data Retention**: Configurable data retention policies

## Installation

### 1. Install Dependencies

```bash
# Install cryptography library for encryption
pip install cryptography

# Install Celery for background tasks
pip install celery redis

# Install DRF Spectacular for API documentation
pip install drf-spectacular
```

### 2. Django Settings

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'core',
    'drf_spectacular',
    'rest_framework',
]
```

Add GPS encryption URLs to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs
    path('api/v1/gps/', include('core.gps_urls')),
]
```

### 3. Database Migration

```bash
# Create migrations for GPS encryption models
python manage.py makemigrations core

# Apply migrations
python manage.py migrate
```

### 4. Settings Configuration

Add these settings to your `settings.py`:

```python
# GPS Encryption Configuration
GPS_SESSION_TIMEOUT = 7200  # 2 hours
GPS_MAX_CONCURRENT_SESSIONS = 1000
GPS_KEY_ROTATION_INTERVAL = 24
GPS_DATA_RETENTION_DAYS = {
    'normal': 30,
    'premium': 90,
    'vip': 365,
    'concierge': 1095
}

# Celery Configuration for Background Tasks
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-gps-sessions': {
        'task': 'core.gps_tasks.cleanup_expired_sessions',
        'schedule': 300.0,  # Every 5 minutes
    },
    'process-gps-data-retention': {
        'task': 'core.gps_tasks.process_data_retention',
        'schedule': 3600.0,  # Every hour
    },
    'monitor-gps-encryption-performance': {
        'task': 'core.gps_tasks.monitor_encryption_performance',
        'schedule': 900.0,  # Every 15 minutes
    },
}

# DRF Spectacular for API documentation
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'VIP Ride-Hailing GPS Encryption API',
    'DESCRIPTION': 'GPS encryption endpoints for secure location tracking',
    'VERSION': '1.0.0',
}
```

### 5. Start Background Services

```bash
# Start Redis server
redis-server

# Start Celery worker (in separate terminal)
celery -A your_project worker --loglevel=info

# Start Celery beat scheduler (in separate terminal)
celery -A your_project beat --loglevel=info
```

## API Usage

### 1. Key Exchange (Start Encryption Session)

```http
POST /api/v1/gps/key-exchange/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "client_public_key": "base64_encoded_client_public_key",
    "ride_id": "uuid_of_ride"
}
```

Response:
```json
{
    "session_id": "encryption_session_id",
    "server_public_key": "base64_encoded_server_public_key",
    "expires_at": "2024-01-15T14:30:00Z",
    "session_timeout": 7200
}
```

### 2. Encrypt GPS Coordinates

```http
POST /api/v1/gps/encrypt/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "session_id": "encryption_session_id",
    "latitude": 6.5244,
    "longitude": 3.3792,
    "timestamp": "2024-01-15T12:30:00Z",
    "speed": 45.5,
    "bearing": 180.0,
    "altitude": 25.0,
    "accuracy": 5.0
}
```

Response:
```json
{
    "success": true,
    "data_id": "uuid_of_encrypted_data",
    "encrypted_at": "2024-01-15T12:30:01Z",
    "message": "GPS data encrypted successfully"
}
```

### 3. Decrypt GPS Coordinates (VIP/Admin Only)

```http
POST /api/v1/gps/decrypt/
Content-Type: application/json
Authorization: Bearer <vip_jwt_token>

{
    "data_ids": ["uuid1", "uuid2", "uuid3"],
    "reason": "Emergency response"
}
```

Response:
```json
{
    "success": true,
    "decrypted_count": 3,
    "failed_count": 0,
    "data": [
        {
            "data_id": "uuid1",
            "latitude": 6.5244,
            "longitude": 3.3792,
            "timestamp": "2024-01-15T12:30:00Z",
            "speed": 45.5,
            "bearing": 180.0,
            "altitude": 25.0,
            "accuracy": 5.0,
            "user_email": "user@example.com",
            "recorded_at": "2024-01-15T12:30:01Z",
            "source_device": "mobile_app"
        }
    ],
    "errors": []
}
```

### 4. Session Status

```http
GET /api/v1/gps/sessions/{session_id}/status/
Authorization: Bearer <jwt_token>
```

### 5. Terminate Session

```http
POST /api/v1/gps/sessions/terminate/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "session_id": "encryption_session_id",
    "reason": "Ride completed"
}
```

## Testing

### Run Built-in Tests

```bash
# Test basic encryption functionality
python manage.py test_gps_encryption --test-type=basic --verbose

# Test performance with 100 data points
python manage.py test_gps_encryption --test-type=performance --data-points=100

# Test concurrent sessions
python manage.py test_gps_encryption --test-type=concurrent --session-count=10

# Run all tests
python manage.py test_gps_encryption --test-type=all
```

### Integration Testing

```python
# Example integration test
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.encryption import GPSEncryptionManager

class GPSEncryptionIntegrationTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            tier='vip'
        )
        self.encryption_manager = GPSEncryptionManager()
    
    def test_full_encryption_cycle(self):
        # Start session
        session_result = self.encryption_manager.start_encryption_session(
            ride_id='test-ride-123',
            client_public_key='test_key'
        )
        self.assertTrue(session_result['success'])
        
        # Encrypt GPS data
        gps_data = {
            'latitude': 6.5244,
            'longitude': 3.3792,
            'timestamp': timezone.now()
        }
        
        encryption_result = self.encryption_manager.encrypt_gps_data(
            session_id=session_result['session_id'],
            gps_data=gps_data
        )
        self.assertTrue(encryption_result['success'])
        
        # Decrypt GPS data
        decryption_result = self.encryption_manager.decrypt_gps_data(
            session_id=session_result['session_id'],
            encrypted_data=encryption_result['encrypted_data'],
            nonce=encryption_result['nonce']
        )
        self.assertTrue(decryption_result['success'])
        
        # Verify data integrity
        decrypted = decryption_result['gps_data']
        self.assertAlmostEqual(decrypted.latitude, gps_data['latitude'], places=6)
        self.assertAlmostEqual(decrypted.longitude, gps_data['longitude'], places=6)
```

## Security Considerations

### 1. Key Management
- Server private keys are stored in memory only
- Session keys are automatically cleared after session expiry
- ECDH key exchange ensures forward secrecy

### 2. Access Control
- Premium/VIP users can encrypt GPS data
- VIP users and admins can decrypt GPS data
- All operations are logged for audit purposes

### 3. Data Protection
- GPS coordinates are encrypted before storage
- Metadata (speed, bearing, etc.) is also encrypted
- Database contains only encrypted data and nonces

### 4. Audit Trail
- All encryption/decryption operations are logged
- Security events are tracked with severity levels
- Failed operations are monitored and alerted

## Monitoring & Maintenance

### 1. Background Tasks
- Monitor Celery workers for proper operation
- Check Redis connection for task queue
- Verify session cleanup is running regularly

### 2. Performance Monitoring
- Track encryption/decryption times
- Monitor session counts and resource usage
- Set up alerts for high failure rates

### 3. Security Monitoring
- Review audit logs for suspicious activity
- Monitor failed decryption attempts
- Check for unauthorized access attempts

### 4. Data Retention
- Configure retention policies per user tier
- Monitor storage usage and cleanup
- Ensure compliance with data protection regulations

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Migration Errors**: Check model dependencies and foreign keys
3. **Encryption Failures**: Verify session exists and hasn't expired
4. **Permission Denied**: Check user tier and authentication
5. **Background Task Issues**: Verify Celery and Redis are running

### Debug Commands

```bash
# Check GPS encryption system status
python manage.py shell -c "from core.encryption import GPSEncryptionManager; print(GPSEncryptionManager().get_system_status())"

# View active sessions
python manage.py shell -c "from core.gps_models import GPSEncryptionSession; print(GPSEncryptionSession.objects.filter(is_active=True).count())"

# Check recent audit events
python manage.py shell -c "from core.gps_models import GPSEncryptionAudit; print(list(GPSEncryptionAudit.objects.order_by('-created_at')[:5].values('event_type', 'severity', 'message')))"
```

## Production Deployment

### 1. Environment Variables
```bash
export GPS_SESSION_TIMEOUT=7200
export GPS_MAX_CONCURRENT_SESSIONS=1000
export CELERY_BROKER_URL=redis://redis:6379/0
```

### 2. Docker Configuration
```dockerfile
# Add to your Dockerfile
RUN pip install cryptography celery redis

# Ensure logs directory exists
RUN mkdir -p /app/logs
```

### 3. Load Balancing
- GPS encryption sessions are stateful
- Use sticky sessions or shared session storage
- Consider Redis cluster for high availability

### 4. Backup & Recovery
- Regular database backups including encrypted GPS data
- Backup encryption audit logs
- Test recovery procedures regularly

## Support

For technical support or questions about the GPS encryption system:

1. Check the audit logs for error details
2. Review the Django logs for system errors
3. Monitor Celery task status for background operations
4. Verify user permissions and tier access
5. Test with the built-in management commands

The system includes comprehensive logging and monitoring to help diagnose issues quickly.
