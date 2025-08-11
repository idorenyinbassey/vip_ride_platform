"""
VIP Ride-Hailing Platform - Pricing App Configuration
Django app configuration for the pricing module
"""

from django.apps import AppConfig


class PricingConfig(AppConfig):
    """Configuration for the pricing app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pricing'
    verbose_name = 'Pricing Management'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Import signals when app is ready - only if the module exists
        try:
            from . import signals  # noqa: F401
        except ImportError as e:
            if 'signals' in str(e):
                # Log that signals module is not found
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Pricing signals module not found - skipping signals import")
            else:
                # Re-raise if it's a different import error
                raise
