# GPS Encryption App Configuration
"""
Django app configuration for GPS encryption system
"""

from django.apps import AppConfig


class GPSEncryptionConfig(AppConfig):
    """Configuration for GPS encryption app"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.gps_encryption'
    verbose_name = 'GPS Encryption System'
    
    def ready(self):
        """Initialize GPS encryption system when Django starts"""
        # Import signal handlers
        try:
            from . import signals
        except ImportError:
            pass
        
        # Initialize encryption manager
        try:
            from core.encryption import GPSEncryptionManager
            # Perform any initialization needed
            pass
        except Exception as e:
            # Log initialization errors but don't crash
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"GPS encryption initialization warning: {e}")


# GPS Encryption Settings Template
GPS_ENCRYPTION_SETTINGS_TEMPLATE = """
# GPS Encryption Configuration
# Add these settings to your Django settings.py file

# GPS encryption session timeout (seconds)
GPS_SESSION_TIMEOUT = 7200  # 2 hours

# Maximum concurrent GPS encryption sessions
GPS_MAX_CONCURRENT_SESSIONS = 1000

# GPS encryption key rotation interval (hours)
GPS_KEY_ROTATION_INTERVAL = 24

# GPS data retention settings
GPS_DATA_RETENTION_DAYS = {
    'normal': 30,
    'premium': 90,
    'vip': 365,
    'concierge': 1095  # 3 years
}

# GPS encryption audit settings
GPS_AUDIT_LOG_RETENTION_DAYS = 1095  # 3 years
GPS_AUDIT_LOG_CRITICAL_EVENTS = True

# GPS encryption performance settings
GPS_ENCRYPTION_BATCH_SIZE = 100
GPS_ENCRYPTION_MAX_RETRIES = 3
GPS_ENCRYPTION_RETRY_DELAY = 60  # seconds

# GPS encryption security settings
GPS_REQUIRE_VIP_FOR_DECRYPTION = True
GPS_ENABLE_LOCATION_ANONYMIZATION = True
GPS_ENCRYPTION_ALGORITHM = 'AES-256-GCM'
GPS_KEY_EXCHANGE_ALGORITHM = 'ECDH-SECP256R1'

# Background task settings for GPS encryption
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

# Logging configuration for GPS encryption
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'gps_encryption_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/gps_encryption.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'gps_security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/gps_security.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'core.encryption': {
            'handlers': ['gps_encryption_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.gps_views': {
            'handlers': ['gps_encryption_file', 'gps_security_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.gps_tasks': {
            'handlers': ['gps_encryption_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
"""
