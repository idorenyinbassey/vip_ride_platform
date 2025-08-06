"""
GPS Tracking App Configuration
"""

from django.apps import AppConfig


class GpsTrackingConfig(AppConfig):
    """Configuration for GPS tracking app"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gps_tracking'
    verbose_name = 'GPS Tracking'
    
    def ready(self):
        """Import signal handlers when app is ready"""
        try:
            import gps_tracking.signals  # noqa
        except ImportError:
            pass
