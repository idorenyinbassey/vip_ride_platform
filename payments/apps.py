from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'Payment Processing'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            from . import signals  # noqa: F401
        except ImportError as e:
            logger.warning(f"Failed to import payments signals: {e}")
