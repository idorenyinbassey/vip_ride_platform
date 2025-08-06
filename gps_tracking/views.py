"""
API Views for GPS Tracking
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
# from django.contrib.gis.geos import Point  # Removed GeoDjango dependency
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.core.cache import cache
from datetime import timedelta
import asyncio
import logging

from .models import (
    GPSLocation, GeofenceZone, GeofenceEvent, 
    RouteOptimization, OfflineGPSBuffer
)
from .serializers import (
    GPSLocationSerializer, GPSLocationCreateSerializer,
    GeofenceZoneSerializer, GeofenceEventSerializer,
    RouteOptimizationSerializer, RouteOptimizationCreateSerializer,
    OfflineGPSBufferSerializer, OfflineGPSSyncSerializer,
    GPSTrackingStatsSerializer
)
from .services import (
    GPSValidationService, GeofenceService, 
    RouteOptimizationService, OfflineGPSService
)
from .permissions import IsVIPUserOrControlCenter, IsDriverOrCustomer

logger = logging.getLogger(__name__)


class GPSLocationPagination(PageNumberPagination):
    """Pagination for GPS locations"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class GPSLocationListCreateView(generics.ListCreateAPIView):
    """
    List and create GPS locations
    GET: List user's GPS locations with filtering
    POST: Create new GPS location
    """
    
    serializer_class = GPSLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = GPSLocationPagination
    
    def get_queryset(self):
        """Get GPS locations for current user with filtering"""
        queryset = GPSLocation.objects.filter(user=self.request.user)
        
        # Filter by ride
        ride_id = self.request.query_params.get('ride_id')
        if ride_id:
            queryset = queryset.filter(ride_id=ride_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(
                server_timestamp__gte=start_date
            )
        if end_date:
            queryset = queryset.filter(
                server_timestamp__lte=end_date
            )
        
        # Filter by accuracy level
        accuracy_level = self.request.query_params.get('accuracy_level')
        if accuracy_level:
            queryset = queryset.filter(accuracy_level=accuracy_level)
        
        return queryset.order_by('-server_timestamp')
    
    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.request.method == 'POST':
            return GPSLocationCreateSerializer
        return GPSLocationSerializer


# Additional views for URL compatibility
class GPSLocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detail view for GPS locations"""
    serializer_class = GPSLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return GPSLocation.objects.filter(user=self.request.user)


class RouteOptimizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detail view for route optimization"""
    serializer_class = RouteOptimizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RouteOptimization.objects.filter(ride__customer=self.request.user)
