from django.apps import AppConfig


class HotelPartnershipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hotel_partnerships'
    verbose_name = 'Hotel Partnerships'

    def ready(self):
        """Import signals when app is ready"""
        try:
            import hotel_partnerships.signals  # noqa: F401
        except ImportError:
            pass
