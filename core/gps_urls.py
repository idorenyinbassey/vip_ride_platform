# GPS Encryption API URLs
"""
URL configuration for GPS encryption endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import gps_views

app_name = 'gps_encryption'

# API URLs
urlpatterns = [
    # Key exchange and session management
    path(
        'key-exchange/',
        gps_views.GPSKeyExchangeView.as_view(),
        name='key_exchange'
    ),
    path(
        'sessions/<str:session_id>/status/',
        gps_views.get_session_status,
        name='session_status'
    ),
    path(
        'sessions/terminate/',
        gps_views.terminate_session,
        name='terminate_session'
    ),
    
    # GPS data encryption/decryption
    path(
        'encrypt/',
        gps_views.GPSEncryptionView.as_view(),
        name='encrypt_gps'
    ),
    path(
        'decrypt/',
        gps_views.GPSDecryptionView.as_view(),
        name='decrypt_gps'
    ),
    
    # Statistics and monitoring
    path(
        'stats/',
        gps_views.GPSEncryptionStatsView.as_view(),
        name='encryption_stats'
    ),
]
