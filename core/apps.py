# Core GPS Encryption App Configuration

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core GPS encryption app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'GPS Encryption Core'
    
    def ready(self):
        """Called when the app is ready"""
        # Import any signals or tasks here if needed
        pass
