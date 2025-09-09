"""
API URLs for VIP Ride-Hailing Platform
"""
from django.urls import path
from .api_views import APIRootView

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
]
