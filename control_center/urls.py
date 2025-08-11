"""
Control Center URL Configuration
Secure API endpoints for emergency response and VIP monitoring
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'incidents', views.EmergencyIncidentViewSet, basename='incident')
router.register(r'vip-sessions', views.VIPMonitoringSessionViewSet, basename='vipsession')

app_name = 'control_center'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Emergency endpoints
    path('api/sos/trigger/', views.trigger_sos, name='trigger_sos'),
    path('api/dashboard/', views.monitoring_dashboard, name='monitoring_dashboard'),
]
