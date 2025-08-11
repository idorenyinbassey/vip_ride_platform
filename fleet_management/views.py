"""
Fleet Management Views
Secure API views for fleet and vehicle management
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count
from django.db import transaction
from decimal import Decimal
import logging

from .models import Vehicle, FleetCompany
from .serializers import (
    VehicleSerializer, VehicleCreateSerializer, VehicleUpdateSerializer,
    FleetCompanySerializer, FleetCompanyCreateSerializer,
    FleetAnalyticsSerializer, VehicleAssignmentSerializer,
    MaintenanceRecordSerializer
)
from accounts.permissions import IsFleetOwner, IsVehicleOwner
from accounts.models import Driver

logger = logging.getLogger(__name__)


class VehicleViewSet(viewsets.ModelViewSet):
    """Vehicle management viewset with security controls"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return VehicleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VehicleUpdateSerializer
        return VehicleSerializer
    
    def get_queryset(self):
        """Filter vehicles based on user permissions"""
        user = self.request.user
        
        # Superuser sees all vehicles
        if user.is_superuser:
            return Vehicle.objects.all().select_related('owner')
        
        # Vehicle owners see their own vehicles
        queryset = Vehicle.objects.filter(owner=user).select_related('owner')
        
        # Fleet managers can see vehicles in their fleet
        try:
            fleet_companies = FleetCompany.objects.filter(owner=user)
            if fleet_companies.exists():
                # Add fleet vehicles to queryset - only vehicles leased to user's fleets
                fleet_vehicles = Vehicle.objects.filter(
                    ownership_status='leased_to_fleet',
                    fleet_company__in=fleet_companies
                ).select_related('owner')
                queryset = queryset.union(fleet_vehicles)
        except Exception as e:
            logger.warning(f"Error accessing fleet vehicles: {e}")
        
        return queryset
    
    def perform_create(self, serializer):
        """Create vehicle with owner assignment"""
        vehicle = serializer.save(owner=self.request.user)
        logger.info(f"Vehicle created: {vehicle.id} by user {self.request.user.id}")
    
    def perform_update(self, serializer):
        """Update vehicle with permission check"""
        vehicle = self.get_object()
        
        # Check ownership or fleet management permission
        if not self._can_modify_vehicle(vehicle):
            raise PermissionDenied("Insufficient permissions to modify vehicle")
        
        updated_vehicle = serializer.save()
        logger.info(f"Vehicle updated: {vehicle.id} by user {self.request.user.id}")
    
    def perform_destroy(self, instance):
        """Soft delete vehicle"""
        if not self._can_modify_vehicle(instance):
            raise PermissionDenied("Insufficient permissions to delete vehicle")
        
        # Soft delete by setting status to retired
        instance.status = 'retired'
        instance.save()
        logger.info(f"Vehicle retired: {instance.id} by user {self.request.user.id}")
    
    def _can_modify_vehicle(self, vehicle):
        """Check if user can modify the vehicle"""
        user = self.request.user
        
        # Vehicle owner can modify
        if vehicle.owner == user:
            return True
        
        # Fleet manager can modify vehicles leased to their fleets
        if hasattr(user, 'fleet_companies'):
            user_fleet_companies = user.fleet_companies.all()
            return (
                vehicle.ownership_status == 'leased_to_fleet' and
                hasattr(vehicle, 'fleet_company') and
                vehicle.fleet_company in user_fleet_companies
            )
        
        return user.is_superuser
    
    @action(detail=True, methods=['post'])
    def assign_driver(self, request, pk=None):
        """Assign driver to vehicle"""
        vehicle = self.get_object()
        serializer = VehicleAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                driver = Driver.objects.get(id=serializer.validated_data['driver_id'])
                
                # Check permissions
                if not self._can_modify_vehicle(vehicle):
                    return Response(
                        {'error': 'Insufficient permissions'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Create assignment (implement assignment model as needed)
                # For now, just return success
                return Response({
                    'status': 'assigned',
                    'vehicle': vehicle.id,
                    'driver': str(driver.id),
                    'assignment_type': serializer.validated_data['assignment_type']
                })
                
            except Driver.DoesNotExist:
                return Response(
                    {'error': 'Driver not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_maintenance(self, request, pk=None):
        """Add maintenance record"""
        vehicle = self.get_object()
        serializer = MaintenanceRecordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not self._can_modify_vehicle(vehicle):
                return Response(
                    {'error': 'Insufficient permissions'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update vehicle maintenance info
            maintenance_data = serializer.validated_data
            vehicle.last_maintenance_date = maintenance_data['maintenance_date']
            vehicle.current_mileage = maintenance_data['mileage_at_service']
            
            if maintenance_data.get('next_maintenance_date'):
                vehicle.next_maintenance_date = maintenance_data['next_maintenance_date']
            
            vehicle.save()
            
            # Log maintenance (implement maintenance model as needed)
            logger.info(f"Maintenance added for vehicle {vehicle.id}")
            
            return Response({
                'status': 'maintenance_recorded',
                'vehicle': str(vehicle.id),
                'maintenance_type': maintenance_data['maintenance_type'],
                'cost': maintenance_data['cost']
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_vehicles(self, request):
        """Get current user's vehicles"""
        vehicles = Vehicle.objects.filter(owner=request.user)
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_vehicles(self, request):
        """Get available vehicles for assignment"""
        vehicles = self.get_queryset().filter(
            status='active'
        ).exclude(
            # Exclude assigned vehicles (implement assignment check)
            id__in=[]  # Add assigned vehicle IDs here
        )
        
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)


class FleetCompanyViewSet(viewsets.ModelViewSet):
    """Fleet company management viewset"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return FleetCompanyCreateSerializer
        return FleetCompanySerializer
    
    def get_queryset(self):
        """Filter fleet companies based on user permissions"""
        user = self.request.user
        
        # Superuser sees all companies
        if user.is_superuser:
            return FleetCompany.objects.all().select_related('owner')
        
        # Users see their own companies
        return FleetCompany.objects.filter(owner=user).select_related('owner')
    
    def perform_create(self, serializer):
        """Create fleet company with owner assignment"""
        company = serializer.save(owner=self.request.user)
        logger.info(f"Fleet company created: {company.id} by user {self.request.user.id}")
    
    def perform_update(self, serializer):
        """Update fleet company with permission check"""
        company = self.get_object()
        
        if company.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Insufficient permissions to modify fleet company")
        
        updated_company = serializer.save()
        logger.info(f"Fleet company updated: {company.id} by user {self.request.user.id}")
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get fleet analytics"""
        company = self.get_object()
        
        # Check permissions
        if company.owner != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate analytics
        vehicles = Vehicle.objects.filter(
            ownership_status='fleet_owned'
            # Add fleet company relationship when implemented
        )
        
        # Current month stats
        current_month = timezone.now().replace(day=1)
        
        analytics_data = {
            'total_revenue': company.monthly_revenue,
            'monthly_revenue': company.monthly_revenue,
            'total_rides': company.total_rides_completed,
            'monthly_rides': company.total_rides_completed,  # Implement monthly filter
            'average_rating': company.average_rating,
            'utilization_rate': company.utilization_rate,
            'top_vehicles': self._get_top_vehicles(company),
            'revenue_trends': self._get_revenue_trends(company),
            'maintenance_alerts': self._get_maintenance_alerts(vehicles)
        }
        
        serializer = FleetAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    def _get_top_vehicles(self, company):
        """Get top performing vehicles"""
        # Implement when ride-vehicle relationship is available
        return [
            {'vehicle_id': 'sample', 'revenue': 50000, 'rides': 100},
            {'vehicle_id': 'sample2', 'revenue': 45000, 'rides': 90}
        ]
    
    def _get_revenue_trends(self, company):
        """Get revenue trends for last 7 days"""
        from datetime import timedelta
        trends = []
        today = timezone.now().date()
        
        for i in range(7):
            day = today - timedelta(days=i)
            # Implement actual revenue calculation per day
            trends.append({
                'date': day.isoformat(),
                'revenue': float(company.monthly_revenue / 30)  # Dummy calculation
            })
        
        return list(reversed(trends))
    
    def _get_maintenance_alerts(self, vehicles):
        """Get vehicles requiring maintenance"""
        alerts = []
        today = timezone.now().date()
        
        for vehicle in vehicles:
            if (vehicle.next_maintenance_date and 
                    vehicle.next_maintenance_date <= today):
                alerts.append({
                    'vehicle_id': str(vehicle.id),
                    'make_model': f"{vehicle.make} {vehicle.model}",
                    'maintenance_due': vehicle.next_maintenance_date.isoformat(),
                    'priority': 'high' if vehicle.next_maintenance_date < today else 'medium'
                })
        
        return alerts
    
    @action(detail=True, methods=['get'])
    def vehicles(self, request, pk=None):
        """Get fleet company vehicles"""
        company = self.get_object()
        
        # Check permissions
        if company.owner != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get vehicles associated with this fleet
        vehicles = Vehicle.objects.filter(
            ownership_status='fleet_owned'
            # Add proper fleet company relationship filter
        )
        
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify_company(self, request, pk=None):
        """Verify fleet company (admin only)"""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        company = self.get_object()
        verification_level = request.data.get('verification_level', 'basic')
        
        with transaction.atomic():
            company.is_verified = True
            company.verification_date = timezone.now()
            company.verification_level = verification_level
            company.save()
        
        logger.info(f"Fleet company verified: {company.id} at level {verification_level}")
        
        return Response({
            'status': 'verified',
            'verification_level': verification_level,
            'verification_date': company.verification_date
        })
    
    @action(detail=False, methods=['get'])
    def verification_pending(self, request):
        """Get companies pending verification (admin only)"""
        if not request.user.is_superuser:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        companies = FleetCompany.objects.filter(
            is_verified=False,
            is_active=True
        )
        
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)
