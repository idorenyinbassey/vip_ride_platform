"""
Fleet Management URL Configuration
Secure API endpoints for fleet and vehicle management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'vehicles', views.VehicleViewSet, basename='vehicle')
router.register(r'companies', views.FleetCompanyViewSet, basename='fleetcompany')

app_name = 'fleet_management'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Additional endpoints can be added here
]
