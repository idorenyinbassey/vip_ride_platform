# rides/workflow_urls.py
"""
VIP Ride-Hailing Platform - Workflow URL Configuration
URL patterns for ride workflow API endpoints
"""

from django.urls import path
from . import workflow_views

app_name = 'ride_workflow'

urlpatterns = [
    # Ride request workflow
    path(
        'request/',
        workflow_views.RideRequestView.as_view(),
        name='request_ride'
    ),
    
    # Driver acceptance workflow
    path(
        '<uuid:ride_id>/accept/',
        workflow_views.DriverAcceptanceView.as_view(),
        name='driver_accept'
    ),
    
    # Ride cancellation
    path(
        '<uuid:ride_id>/cancel/',
        workflow_views.RideCancellationView.as_view(),
        name='cancel_ride'
    ),
    
    # Status updates
    path(
        '<uuid:ride_id>/status/',
        workflow_views.RideStatusUpdateView.as_view(),
        name='update_status'
    ),
    
    # Ride completion
    path(
        '<uuid:ride_id>/complete/',
        workflow_views.RideCompletionView.as_view(),
        name='complete_ride'
    ),
    
    # Status history
    path(
        '<uuid:ride_id>/history/',
        workflow_views.RideStatusHistoryView.as_view(),
        name='status_history'
    ),
    
    # Workflow status details
    path(
        '<uuid:ride_id>/workflow/',
        workflow_views.ride_workflow_status,
        name='workflow_status'
    ),
    
    # User's active rides
    path(
        'active/',
        workflow_views.user_active_rides,
        name='active_rides'
    ),
    
    # Cancellation policy
    path(
        'cancellation-policy/',
        workflow_views.CancellationPolicyView.as_view(),
        name='cancellation_policy'
    ),
    path(
        '<uuid:ride_id>/cancellation-policy/',
        workflow_views.CancellationPolicyView.as_view(),
        name='ride_cancellation_policy'
    ),
    
    # VIP SOS trigger
    path(
        '<uuid:ride_id>/sos/',
        workflow_views.trigger_sos,
        name='trigger_sos'
    ),
]
