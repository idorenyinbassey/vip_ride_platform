"""
API Root Views for VIP Ride-Hailing Platform

Provides Django REST Framework class-based API root view for endpoint discovery.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class APIRootView(APIView):
    """
    VIP Ride-Hailing Platform API Root
    
    Welcome to the VIP Ride-Hailing Platform API! This API provides comprehensive
    endpoints for managing rides, users, payments, fleet operations, and more.
    
    ## API Features
    - Multi-tier user system (Normal/Premium/VIP)
    - Real-time GPS tracking with encryption
    - Hotel partnership integration  
    - Fleet and vehicle management
    - Emergency response system
    - Payment processing
    - Comprehensive notifications
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        """
        Return API root with links to all available endpoints
        """
        return Response({
            'message': 'Welcome to VIP Ride-Hailing Platform API',
            'version': 'v1',
            'description': 'Multi-tier ride-hailing platform with Normal, Premium, and VIP services',
            'platform_features': [
                'Multi-tier user system (Normal/Premium/VIP)',
                'Real-time GPS tracking with AES-256-GCM encryption',
                'Hotel partnership integration',
                'Fleet management system',
                'Emergency response (SOS)',
                'Vehicle leasing marketplace',
                'Multi-gateway payment processing',
                'Control center monitoring',
                'Comprehensive notifications'
            ],
            'api_endpoints': {
                'accounts': request.build_absolute_uri('/api/v1/accounts/'),
                'rides': request.build_absolute_uri('/api/v1/rides/'),
                'fleet': request.build_absolute_uri('/api/v1/fleet/'),
                'leasing': request.build_absolute_uri('/api/v1/leasing/'),
                'hotel_partnerships': request.build_absolute_uri('/api/v1/hotel-partnerships/'),
                'payments': request.build_absolute_uri('/api/v1/payments/'),
                'pricing': request.build_absolute_uri('/api/v1/pricing/'),
                'notifications': request.build_absolute_uri('/api/v1/notifications/'),
                'control_center': request.build_absolute_uri('/api/v1/control-center/'),
                'gps_tracking': request.build_absolute_uri('/api/v1/gps/'),
            },
            'platform_services': {
                'metrics': request.build_absolute_uri('/metrics'),
                'health_check': request.build_absolute_uri('/health/'),
                'admin_panel': request.build_absolute_uri('/admin/'),
                'api_browser': request.build_absolute_uri('/api-auth/'),
            },
            'user_tiers': {
                'normal': 'Standard rides, basic booking (15-20% commission)',
                'premium': 'Luxury cars, hotel booking (20-25% commission)', 
                'vip': 'Encrypted GPS, SOS, trusted drivers (25-30% commission)'
            },
            'driver_categories': {
                'private_drivers': 'Private drivers with classic cars',
                'fleet_companies': 'Fleet companies with premium cars/vans',
                'vehicle_owners': 'Vehicle owners for leasing marketplace'
            },
            'authentication': {
                'method': 'JWT Bearer Token',
                'login': request.build_absolute_uri('/api-auth/login/'),
                'logout': request.build_absolute_uri('/api-auth/logout/'),
            },
            'rate_limiting': {
                'enabled': True,
                'default_limit': '1000/hour per user',
                'anonymous_limit': '100/hour per IP'
            },
            'api_documentation': {
                'browsable_api': request.build_absolute_uri('/api/v1/'),
                'admin_interface': request.build_absolute_uri('/admin/'),
                'prometheus_metrics': request.build_absolute_uri('/metrics')
            }
        }, status=status.HTTP_200_OK)
