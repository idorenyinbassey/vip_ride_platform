from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import logging

from .models import VehicleLease, LeasePayment
from .serializers import (
    VehicleListingSerializer,
    LeaseCalculationSerializer, VehicleSearchSerializer,
    VehicleLeaseSerializer, LeasePaymentSerializer
)
from .services import VehicleLeasingService
from fleet_management.models import Vehicle, FleetCompany
from accounts.permissions import TierBasedPermission

logger = logging.getLogger(__name__)


class IsFleetOwnerOrAdmin(TierBasedPermission):
    """Permission for fleet owners and admins"""
    required_tier = 'premium'


class VehicleListingViewSet(viewsets.ModelViewSet):
    """ViewSet for available vehicles that can be leased"""
    queryset = Vehicle.objects.filter(status='active')
    serializer_class = VehicleListingSerializer
    permission_classes = [IsAuthenticated, IsFleetOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'make', 'fuel_type', 'engine_type']
    search_fields = ['make', 'model', 'license_plate']
    ordering_fields = ['year', 'make', 'model']
    ordering = ['-year']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        
        if self.request.user.user_type == 'fleet_company':
            # Fleet companies can see all available vehicles
            queryset = queryset.filter(status='active')
        
        return queryset


class VehicleLeaseViewSet(viewsets.ModelViewSet):
    """ViewSet for vehicle lease contracts"""
    queryset = VehicleLease.objects.select_related(
        'vehicle_owner', 'fleet_company', 'vehicle'
    ).prefetch_related('lease_payments')
    serializer_class = VehicleLeaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'revenue_share_model', 'maintenance_responsibility']
    search_fields = ['vehicle__license_plate', 'vehicle__make', 'vehicle__model']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_staff:
            return queryset
        elif user.user_type == 'vehicle_owner':
            return queryset.filter(vehicle_owner=user)
        elif user.user_type == 'fleet_company':
            try:
                fleet = FleetCompany.objects.get(owner=user)
                return queryset.filter(fleet_company=fleet)
            except FleetCompany.DoesNotExist:
                return queryset.none()
        else:
            return queryset.none()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a lease contract"""
        lease = self.get_object()
        
        if lease.status != VehicleLease.LeaseStatus.PENDING_APPROVAL:
            return Response(
                {'error': 'Only pending leases can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lease.status = VehicleLease.LeaseStatus.ACTIVE
        lease.save()
        
        # Mark vehicle as unavailable
        lease.vehicle.status = 'maintenance'
        lease.vehicle.save()
        
        return Response({'message': 'Lease approved successfully'})

    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a lease contract"""
        lease = self.get_object()
        
        if lease.status not in [VehicleLease.LeaseStatus.ACTIVE, VehicleLease.LeaseStatus.SUSPENDED]:
            return Response(
                {'error': 'Only active or suspended leases can be terminated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lease.status = VehicleLease.LeaseStatus.TERMINATED
        lease.save()
        
        # Mark vehicle as available again
        lease.vehicle.status = 'active'
        lease.vehicle.save()
        
        return Response({'message': 'Lease terminated successfully'})

    @action(detail=True, methods=['get'])
    def revenue_report(self, request, pk=None):
        """Get revenue report for a lease"""
        lease = self.get_object()
        
        # Calculate total revenue
        total_revenue = lease.lease_payments.filter(
            payment_type='revenue_share'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate monthly breakdown
        payments = lease.lease_payments.filter(
            payment_type='revenue_share'
        ).annotate(
            month=TruncMonth('due_date')
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'lease_id': lease.id,
            'total_revenue': total_revenue,
            'monthly_breakdown': list(payments),
            'lease_status': lease.status
        })


class LeasePaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for lease payments"""
    queryset = LeasePayment.objects.select_related('lease')
    serializer_class = LeasePaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_type', 'status']
    ordering_fields = ['due_date', 'amount', 'created_at']
    ordering = ['-due_date']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """Filter based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_staff:
            return queryset
        elif user.user_type == 'vehicle_owner':
            return queryset.filter(lease__vehicle_owner=user)
        elif user.user_type == 'fleet_company':
            try:
                fleet = FleetCompany.objects.get(owner=user)
                return queryset.filter(lease__fleet_company=fleet)
            except FleetCompany.DoesNotExist:
                return queryset.none()
        else:
            return queryset.none()

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a payment as paid"""
        payment = self.get_object()
        
        if payment.status == LeasePayment.PaymentStatus.PAID:
            return Response(
                {'error': 'Payment is already marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = LeasePayment.PaymentStatus.PAID
        payment.paid_date = timezone.now().date()
        payment.save()
        
        return Response({'message': 'Payment marked as paid successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_lease(request):
    """Calculate lease pricing and terms"""
    try:
        serializer = LeaseCalculationSerializer(data=request.data)
        if serializer.is_valid():
            service = VehicleLeasingService()
            calculation = service.calculate_lease_terms(
                vehicle_id=serializer.validated_data['vehicle_id'],
                revenue_share_model=serializer.validated_data['revenue_share_model'],
                **serializer.validated_data
            )
            return Response(calculation)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Lease calculation error: {str(e)}")
        return Response(
            {'error': 'Failed to calculate lease terms'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_vehicles(request):
    """Search for available vehicles for leasing"""
    try:
        serializer = VehicleSearchSerializer(data=request.GET)
        if serializer.is_valid():
            queryset = Vehicle.objects.filter(status='active')
            
            # Apply filters
            filters = serializer.validated_data
            if filters.get('vehicle_type'):
                queryset = queryset.filter(category=filters['vehicle_type'])
            if filters.get('brand'):
                queryset = queryset.filter(make__icontains=filters['brand'])
            if filters.get('fuel_type'):
                queryset = queryset.filter(fuel_type=filters['fuel_type'])
            if filters.get('transmission'):
                queryset = queryset.filter(engine_type=filters['transmission'])
            
            # Serialize results
            vehicles = VehicleListingSerializer(queryset[:20], many=True).data
            
            return Response({
                'vehicles': vehicles,
                'total_found': queryset.count()
            })
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Vehicle search error: {str(e)}")
        return Response(
            {'error': 'Failed to search vehicles'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_dashboard(request):
    """Get dashboard data for vehicle owners"""
    try:
        if request.user.user_type != 'vehicle_owner':
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get owner's leases
        leases = VehicleLease.objects.filter(vehicle_owner=request.user)
        
        # Calculate statistics
        total_leases = leases.count()
        active_leases = leases.filter(status=VehicleLease.LeaseStatus.ACTIVE).count()
        
        # Calculate earnings from lease payments
        total_earnings = LeasePayment.objects.filter(
            lease__vehicle_owner=request.user,
            status=LeasePayment.PaymentStatus.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get recent payments
        recent_payments = LeasePayment.objects.filter(
            lease__vehicle_owner=request.user
        ).order_by('-created_at')[:5]
        
        recent_payments_data = LeasePaymentSerializer(recent_payments, many=True).data
        
        return Response({
            'total_leases': total_leases,
            'active_leases': active_leases,
            'total_earnings': total_earnings,
            'recent_payments': recent_payments_data
        })
        
    except Exception as e:
        logger.error(f"Owner dashboard error: {str(e)}")
        return Response(
            {'error': 'Failed to get dashboard data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fleet_dashboard(request):
    """Get dashboard data for fleet companies"""
    try:
        try:
            fleet = FleetCompany.objects.get(owner=request.user)
        except FleetCompany.DoesNotExist:
            return Response(
                {'error': 'Fleet company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get fleet's leases
        leases = VehicleLease.objects.filter(fleet_company=fleet)
        
        # Calculate statistics
        total_leases = leases.count()
        active_leases = leases.filter(status=VehicleLease.LeaseStatus.ACTIVE).count()
        
        # Calculate earnings
        total_payments = LeasePayment.objects.filter(
            lease__fleet_company=fleet,
            status=LeasePayment.PaymentStatus.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get vehicle utilization
        total_vehicles = Vehicle.objects.filter(fleet_company=fleet).count()
        leased_vehicles = leases.filter(
            status=VehicleLease.LeaseStatus.ACTIVE
        ).count()
        
        utilization_rate = (leased_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0
        
        return Response({
            'total_leases': total_leases,
            'active_leases': active_leases,
            'total_payments': total_payments,
            'total_vehicles': total_vehicles,
            'leased_vehicles': leased_vehicles,
            'utilization_rate': round(utilization_rate, 2)
        })
        
    except Exception as e:
        logger.error(f"Fleet dashboard error: {str(e)}")
        return Response(
            {'error': 'Failed to get dashboard data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
