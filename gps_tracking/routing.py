"""
WebSocket routing for GPS tracking
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # GPS tracking for individual users
    re_path(r'ws/gps-tracking/$', consumers.GPSTrackingConsumer.as_asgi()),
    
    # Control center monitoring
    re_path(r'ws/control-center/$', consumers.ControlCenterConsumer.as_asgi()),
    
    # Ride-specific tracking
    re_path(r'ws/ride-tracking/(?P<ride_id>[0-9a-f-]+)/$', consumers.RideTrackingConsumer.as_asgi()),
]
