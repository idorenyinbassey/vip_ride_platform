from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count
from decimal import Decimal
import uuid

from .models import (
    Hotel, HotelStaff, HotelRoom, HotelGuest, HotelBooking,
    HotelCommissionReport, BulkBookingEvent, PMSIntegrationLog
)
from .serializers import (
    HotelSerializer, HotelStaffSerializer, HotelRoomSerializer,
    HotelGuestSerializer, HotelBookingSerializer, HotelBookingCreateSerializer,
    BulkBookingEventSerializer, HotelCommissionReportSerializer,
    BookingQuoteSerializer, BookingQuoteResponseSerializer,
    BookingStatusUpdateSerializer, PMSIntegrationLogSerializer
)
from .permissions import IsHotelStaff, IsHotelStaffOrReadOnly


class HotelViewSet(viewsets.ModelViewSet):
    """Hotel management viewset"""
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter hotels based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return Hotel.objects.all()
        
        # Hotel staff can only see their own hotel
        try:
            hotel_staff = HotelStaff.objects.get(user=user, is_active=True)
            return Hotel.objects.filter(id=hotel_staff.hotel.id)
        except HotelStaff.DoesNotExist:
            return Hotel.objects.none()
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get hotel analytics"""
        hotel = self.get_object()
        
        # Check permission
        if not self._can_view_analytics(request.user, hotel):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate analytics
        bookings = HotelBooking.objects.filter(hotel=hotel)
        
        # Current month stats
        current_month = timezone.now().replace(day=1)
        month_bookings = bookings.filter(created_at__gte=current_month)
        
        analytics_data = {
            'total_bookings': bookings.count(),
            'month_bookings': month_bookings.count(),
            'completed_bookings': bookings.filter(status='COMPLETED').count(),
            'pending_bookings': bookings.filter(status='PENDING').count(),
            'total_commission': bookings.aggregate(
                total=Sum('hotel_commission')
            )['total'] or Decimal('0.00'),
            'month_commission': month_bookings.aggregate(
                total=Sum('hotel_commission')
            )['total'] or Decimal('0.00'),
            'average_rating': 4.5,  # TODO: Integrate with rating system
            'top_destinations': self._get_top_destinations(hotel),
            'booking_trends': self._get_booking_trends(hotel)
        }
        
        return Response(analytics_data)
    
    def _can_view_analytics(self, user, hotel):
        """Check if user can view hotel analytics"""
        if user.is_superuser:
            return True
        
        try:
            staff = HotelStaff.objects.get(user=user, hotel=hotel, is_active=True)
            return staff.can_view_analytics
        except HotelStaff.DoesNotExist:
            return False
    
    def _get_top_destinations(self, hotel):
        """Get top 5 destinations for hotel"""
        destinations = (
            HotelBooking.objects
            .filter(hotel=hotel, status='COMPLETED')
            .values('destination')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        return list(destinations)
    
    def _get_booking_trends(self, hotel):
        """Get booking trends for the last 7 days"""
        from datetime import timedelta
        trends = []
        today = timezone.now().date()
        
        for i in range(7):
            day = today - timedelta(days=i)
            count = HotelBooking.objects.filter(
                hotel=hotel,
                created_at__date=day
            ).count()
            trends.append({
                'date': day.isoformat(),
                'bookings': count
            })
        
        return list(reversed(trends))


class HotelStaffViewSet(viewsets.ModelViewSet):
    """Hotel staff management viewset"""
    queryset = HotelStaff.objects.all()
    serializer_class = HotelStaffSerializer
    permission_classes = [IsHotelStaff]
    
    def get_queryset(self):
        """Filter staff based on hotel"""
        user = self.request.user
        if user.is_superuser:
            return HotelStaff.objects.all()
        
        try:
            hotel_staff = HotelStaff.objects.get(user=user, is_active=True)
            return HotelStaff.objects.filter(hotel=hotel_staff.hotel)
        except HotelStaff.DoesNotExist:
            return HotelStaff.objects.none()


class HotelRoomViewSet(viewsets.ModelViewSet):
    """Hotel room management viewset"""
    queryset = HotelRoom.objects.all()
    serializer_class = HotelRoomSerializer
    permission_classes = [IsHotelStaffOrReadOnly]
    
    def get_queryset(self):
        """Filter rooms based on hotel"""
        hotel_id = self.request.query_params.get('hotel')
        if hotel_id:
            return HotelRoom.objects.filter(hotel_id=hotel_id)
        return HotelRoom.objects.all()


class HotelGuestViewSet(viewsets.ModelViewSet):
    """Hotel guest management viewset"""
    queryset = HotelGuest.objects.all()
    serializer_class = HotelGuestSerializer
    permission_classes = [IsHotelStaffOrReadOnly]
    
    def get_queryset(self):
        """Filter guests based on hotel and search parameters"""
        queryset = HotelGuest.objects.all()
        
        # Filter by hotel
        hotel_id = self.request.query_params.get('hotel')
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        
        # Filter by current guests
        current_only = self.request.query_params.get('current_only')
        if current_only:
            today = timezone.now().date()
            queryset = queryset.filter(
                check_in_date__lte=today,
                check_out_date__gte=today,
                is_checked_in=True
            )
        
        # Search by name, phone, room
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(room__room_number__icontains=search)
            )
        
        return queryset


class HotelBookingViewSet(viewsets.ModelViewSet):
    """Hotel booking management viewset"""
    queryset = HotelBooking.objects.all()
    permission_classes = [IsHotelStaff]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HotelBookingCreateSerializer
        return HotelBookingSerializer
    
    def get_queryset(self):
        """Filter bookings based on hotel and parameters"""
        user = self.request.user
        
        # Get user's hotel
        try:
            hotel_staff = HotelStaff.objects.get(user=user, is_active=True)
            queryset = HotelBooking.objects.filter(hotel=hotel_staff.hotel)
        except HotelStaff.DoesNotExist:
            if user.is_superuser:
                queryset = HotelBooking.objects.all()
            else:
                return HotelBooking.objects.none()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(pickup_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(pickup_datetime__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create booking with automatic commission calculation"""
        # Get staff and hotel
        try:
            hotel_staff = HotelStaff.objects.get(
                user=self.request.user, is_active=True
            )
        except HotelStaff.DoesNotExist:
            raise ValidationError("User is not authorized hotel staff")
        
        # Save booking
        booking = serializer.save(
            hotel=hotel_staff.hotel,
            booked_by_staff=hotel_staff
        )
        
        # Get price quote and calculate commission
        self._calculate_pricing(booking)
        booking.save()
    
    def _calculate_pricing(self, booking):
        """Calculate pricing and commission for booking"""
        # TODO: Integrate with pricing system
        # For now, use dummy calculation
        base_fare = Decimal('2500.00')
        surge_multiplier = Decimal('1.5')
        
        estimated_fare = base_fare * surge_multiplier
        booking.estimated_fare = estimated_fare
        
        # Calculate commission
        commission = booking.calculate_commission()
        return commission
    
    @action(detail=False, methods=['post'])
    def get_quote(self, request):
        """Get pricing quote for a potential booking"""
        serializer = BookingQuoteSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Integrate with main pricing system
            quote_data = self._generate_quote(serializer.validated_data)
            response_serializer = BookingQuoteResponseSerializer(quote_data)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_quote(self, quote_request):
        """Generate pricing quote"""
        # Dummy implementation - integrate with real pricing engine
        base_fare = Decimal('2500.00')
        surge_multiplier = Decimal('1.5')
        estimated_fare = base_fare * surge_multiplier
        
        # Get hotel commission rate
        try:
            hotel_staff = HotelStaff.objects.get(
                user=self.request.user, is_active=True
            )
            commission_rate = hotel_staff.hotel.commission_rate
        except HotelStaff.DoesNotExist:
            commission_rate = Decimal('12.50')
        
        hotel_commission = estimated_fare * (commission_rate / 100)
        
        return {
            'estimated_fare': estimated_fare,
            'estimated_duration': timezone.timedelta(minutes=25),
            'distance_km': Decimal('12.5'),
            'base_fare': base_fare,
            'surge_multiplier': surge_multiplier,
            'hotel_commission': hotel_commission,
            'commission_rate': commission_rate,
            'breakdown': {
                'base_fare': base_fare,
                'surge_multiplier': surge_multiplier,
                'total_fare': estimated_fare,
                'hotel_commission': hotel_commission
            }
        }
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update booking status with notification"""
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Update status
            booking.add_status_update(
                status=data['status'],
                message=data['message'],
                user=request.user
            )
            
            # Update driver details if provided
            if 'driver_details' in data:
                booking.driver_assigned = data['driver_details']
                booking.save()
            
            # Send notification to hotel (implement webhook/notification)
            self._send_hotel_notification(booking, data)
            
            return Response({
                'status': 'updated',
                'booking_reference': booking.booking_reference
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_hotel_notification(self, booking, update_data):
        """Send real-time update to hotel"""
        # TODO: Implement WebSocket or webhook notification
        # This would integrate with hotel PMS systems
        pass


class BulkBookingEventViewSet(viewsets.ModelViewSet):
    """Bulk booking event management viewset"""
    queryset = BulkBookingEvent.objects.all()
    serializer_class = BulkBookingEventSerializer
    permission_classes = [IsHotelStaff]
    
    def get_queryset(self):
        """Filter events by hotel"""
        user = self.request.user
        try:
            hotel_staff = HotelStaff.objects.get(user=user, is_active=True)
            return BulkBookingEvent.objects.filter(hotel=hotel_staff.hotel)
        except HotelStaff.DoesNotExist:
            if user.is_superuser:
                return BulkBookingEvent.objects.all()
            return BulkBookingEvent.objects.none()
    
    def perform_create(self, serializer):
        """Create event with hotel and creator"""
        try:
            hotel_staff = HotelStaff.objects.get(
                user=self.request.user, is_active=True
            )
            serializer.save(
                hotel=hotel_staff.hotel,
                created_by=hotel_staff
            )
        except HotelStaff.DoesNotExist:
            raise ValidationError("User is not authorized hotel staff")
    
    @action(detail=True, methods=['post'])
    def create_bookings(self, request, pk=None):
        """Create multiple bookings for an event"""
        event = self.get_object()
        booking_data = request.data.get('bookings', [])
        
        if not booking_data:
            return Response(
                {'error': 'No booking data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_bookings = []
        bulk_group_id = uuid.uuid4()
        
        for booking_info in booking_data:
            booking_serializer = HotelBookingCreateSerializer(data={
                **booking_info,
                'hotel': event.hotel.id,
                'booking_type': 'BULK_EVENT',
                'event_name': event.event_name,
                'bulk_booking_group': bulk_group_id
            })
            
            if booking_serializer.is_valid():
                booking = booking_serializer.save(
                    hotel=event.hotel,
                    booked_by_staff=HotelStaff.objects.get(
                        user=request.user, is_active=True
                    ),
                    bulk_booking_group=bulk_group_id
                )
                created_bookings.append(booking.booking_reference)
            else:
                return Response(
                    booking_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response({
            'event': event.event_name,
            'bookings_created': len(created_bookings),
            'booking_references': created_bookings,
            'bulk_group_id': str(bulk_group_id)
        })


class HotelCommissionReportViewSet(viewsets.ReadOnlyModelViewSet):
    """Hotel commission report viewset"""
    queryset = HotelCommissionReport.objects.all()
    serializer_class = HotelCommissionReportSerializer
    permission_classes = [IsHotelStaff]
    
    def get_queryset(self):
        """Filter reports by hotel"""
        user = self.request.user
        try:
            hotel_staff = HotelStaff.objects.get(user=user, is_active=True)
            return HotelCommissionReport.objects.filter(hotel=hotel_staff.hotel)
        except HotelStaff.DoesNotExist:
            if user.is_superuser:
                return HotelCommissionReport.objects.all()
            return HotelCommissionReport.objects.none()


class PMSIntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """PMS integration log viewset"""
    queryset = PMSIntegrationLog.objects.all()
    serializer_class = PMSIntegrationLogSerializer
    permission_classes = [IsHotelStaff]
    
    def get_queryset(self):
        """Filter logs by hotel"""
        user = self.request.user
        try:
            hotel_staff = HotelStaff.objects.get(user=user, is_active=True)
            return PMSIntegrationLog.objects.filter(hotel=hotel_staff.hotel)
        except HotelStaff.DoesNotExist:
            if user.is_superuser:
                return PMSIntegrationLog.objects.all()
            return PMSIntegrationLog.objects.none()


# Customer-facing views (consolidated from hotels app)
from math import radians, cos, sin, asin, sqrt

class CustomerHotelViewSet(viewsets.ReadOnlyModelViewSet):
    """Customer-facing hotel views with search and discovery"""
    queryset = Hotel.objects.filter(status='ACTIVE')
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search hotels with filters"""
        queryset = self.get_queryset()
        
        # Apply filters
        location = request.GET.get('location')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = request.GET.get('guests', 1)
        
        if location:
            queryset = queryset.filter(
                Q(name__icontains=location) |
                Q(address__icontains=location) |
                Q(city__icontains=location)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get nearby hotels based on coordinates"""
        lat = request.GET.get('latitude')
        lng = request.GET.get('longitude')
        
        if not lat or not lng:
            return Response({'error': 'Latitude and longitude required'}, status=400)
        
        queryset = self.get_queryset()
        # Implement distance calculation and filtering
        serializer = self.get_serializer(queryset[:10], many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular hotels"""
        queryset = self.get_queryset().annotate(
            booking_count=Count('hotelbooking')
        ).order_by('-booking_count')[:10]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CustomerHotelBookingViewSet(viewsets.ModelViewSet):
    """Customer hotel booking management"""
    serializer_class = HotelBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only show user's own bookings"""
        return HotelBooking.objects.filter(
            guest__user=self.request.user
        ).select_related('hotel', 'room', 'guest')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        if booking.status not in ['CANCELLED', 'CHECKED_OUT']:
            booking.status = 'CANCELLED'
            booking.save()
            return Response({'status': 'cancelled'})
        return Response({'error': 'Cannot cancel'}, status=400)
