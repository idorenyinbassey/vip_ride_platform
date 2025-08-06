# URL Configuration for Ride Matching
"""
URL patterns for ride matching API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .matching_views import RideMatchingViewSet

# Create router for matching endpoints
router = DefaultRouter()
router.register(r'matching', RideMatchingViewSet, basename='ride-matching')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional matching endpoints
    path(
        'matching/request-ride/',
        RideMatchingViewSet.as_view({'post': 'request_ride'}),
        name='request-ride'
    ),
    path(
        'matching/driver-response/',
        RideMatchingViewSet.as_view({'post': 'driver_response'}),
        name='driver-response'
    ),
    path(
        'matching/active-offers/',
        RideMatchingViewSet.as_view({'get': 'active_offers'}),
        name='active-offers'
    ),
    path(
        'matching/driver-status/',
        RideMatchingViewSet.as_view({'patch': 'driver_status'}),
        name='driver-status'
    ),
    path(
        'matching/surge-zones/',
        RideMatchingViewSet.as_view({'get': 'surge_zones'}),
        name='surge-zones'
    ),
    path(
        'matching/stats/',
        RideMatchingViewSet.as_view({'get': 'matching_stats'}),
        name='matching-stats'
    ),
    path(
        'matching/<uuid:pk>/status/',
        RideMatchingViewSet.as_view({'get': 'ride_status'}),
        name='ride-status'
    ),
    path(
        'matching/cancel/',
        RideMatchingViewSet.as_view({'post': 'cancel_ride'}),
        name='cancel-ride'
    ),
]
