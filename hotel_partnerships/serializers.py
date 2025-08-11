from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Hotel, HotelStaff, HotelRoom, HotelGuest, HotelBooking,
    HotelCommissionReport, BulkBookingEvent, PMSIntegrationLog
)


class HotelSerializer(serializers.ModelSerializer):
    """Hotel information serializer"""
    full_address = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    booking_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'brand', 'tier', 'status', 'full_address',
            'city', 'state', 'latitude', 'longitude', 'phone', 'email',
            'star_rating', 'total_rooms', 'commission_rate',
            'preferred_vehicle_types', 'is_active', 'booking_count',
            'auto_assign_rides', 'guest_booking_enabled'
        ]
        read_only_fields = ['id']
    
    def get_booking_count(self, obj):
        return obj.bookings.count()


class HotelStaffSerializer(serializers.ModelSerializer):
    """Hotel staff serializer"""
    user_details = serializers.SerializerMethodField()
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    can_make_bookings = serializers.ReadOnlyField()
    can_view_analytics = serializers.ReadOnlyField()
    
    class Meta:
        model = HotelStaff
        fields = [
            'id', 'user', 'user_details', 'hotel', 'hotel_name',
            'role', 'permission_level', 'department', 'employee_id',
            'phone', 'extension', 'is_active', 'can_make_bookings',
            'can_view_analytics', 'last_login'
        ]
        read_only_fields = ['id', 'last_login']
    
    def get_user_details(self, obj):
        return {
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email
        }


class HotelRoomSerializer(serializers.ModelSerializer):
    """Hotel room serializer"""
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    
    class Meta:
        model = HotelRoom
        fields = [
            'id', 'hotel', 'hotel_name', 'room_number', 'room_type',
            'floor', 'capacity', 'amenities', 'has_balcony',
            'has_kitchenette', 'status', 'base_rate'
        ]
        read_only_fields = ['id']


class HotelGuestSerializer(serializers.ModelSerializer):
    """Hotel guest serializer"""
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    full_name = serializers.ReadOnlyField()
    is_current_guest = serializers.ReadOnlyField()
    
    class Meta:
        model = HotelGuest
        fields = [
            'id', 'hotel', 'hotel_name', 'room', 'room_number',
            'first_name', 'last_name', 'full_name', 'email', 'phone',
            'guest_type', 'check_in_date', 'check_out_date',
            'number_of_guests', 'preferred_vehicle_type',
            'special_requests', 'is_checked_in', 'is_vip',
            'is_current_guest', 'pms_guest_id'
        ]
        read_only_fields = ['id']


class HotelBookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating hotel bookings"""
    
    class Meta:
        model = HotelBooking
        fields = [
            'hotel', 'guest', 'booked_by_staff', 'booking_type',
            'guest_name', 'guest_phone', 'guest_room_number',
            'pickup_location', 'pickup_latitude', 'pickup_longitude',
            'destination', 'destination_latitude', 'destination_longitude',
            'pickup_datetime', 'vehicle_type', 'passenger_count',
            'special_instructions', 'priority', 'event_name'
        ]
    
    def validate(self, data):
        """Validate booking data"""
        # Ensure pickup time is in the future
        from django.utils import timezone
        if data['pickup_datetime'] <= timezone.now():
            raise serializers.ValidationError({
                'pickup_datetime': 'Pickup time must be in the future'
            })
        
        # Validate passenger count
        if data['passenger_count'] < 1 or data['passenger_count'] > 8:
            raise serializers.ValidationError({
                'passenger_count': 'Passenger count must be between 1 and 8'
            })
        
        return data


class HotelBookingSerializer(serializers.ModelSerializer):
    """Full hotel booking serializer"""
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    guest_full_name = serializers.CharField(source='guest.full_name', read_only=True)
    booked_by = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = HotelBooking
        fields = [
            'id', 'booking_reference', 'hotel', 'hotel_name',
            'guest', 'guest_full_name', 'booked_by_staff', 'booked_by',
            'booking_type', 'guest_name', 'guest_phone', 'guest_room_number',
            'pickup_location', 'pickup_latitude', 'pickup_longitude',
            'destination', 'destination_latitude', 'destination_longitude',
            'pickup_datetime', 'estimated_duration', 'vehicle_type',
            'passenger_count', 'special_instructions', 'estimated_fare',
            'final_fare', 'hotel_commission', 'commission_rate_used',
            'status', 'status_display', 'priority', 'ride_id',
            'driver_assigned', 'status_updates', 'event_name',
            'bulk_booking_group', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'booking_reference', 'hotel_commission',
            'commission_rate_used', 'status_updates', 'created_at',
            'updated_at', 'completed_at'
        ]
    
    def get_booked_by(self, obj):
        if obj.booked_by_staff:
            return {
                'name': obj.booked_by_staff.user.get_full_name(),
                'role': obj.booked_by_staff.role
            }
        return None


class BulkBookingEventSerializer(serializers.ModelSerializer):
    """Bulk booking event serializer"""
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    booking_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BulkBookingEvent
        fields = [
            'id', 'hotel', 'hotel_name', 'event_name', 'event_type',
            'description', 'event_date', 'start_time', 'end_time',
            'expected_guests', 'pickup_locations', 'destination_venue',
            'vehicle_types_needed', 'estimated_rides', 'special_requirements',
            'event_coordinator_name', 'event_coordinator_phone',
            'event_coordinator_email', 'status', 'estimated_total_cost',
            'actual_total_cost', 'created_by', 'created_by_name',
            'booking_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.user.get_full_name()
        return None
    
    def get_booking_count(self, obj):
        return HotelBooking.objects.filter(bulk_booking_group=obj.id).count()


class HotelCommissionReportSerializer(serializers.ModelSerializer):
    """Hotel commission report serializer"""
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    
    class Meta:
        model = HotelCommissionReport
        fields = [
            'id', 'hotel', 'hotel_name', 'report_month',
            'total_bookings', 'completed_bookings', 'cancelled_bookings',
            'total_ride_value', 'total_commission_earned',
            'average_commission_rate', 'average_rating',
            'response_time_avg', 'status', 'payment_due_date',
            'payment_made_date', 'payment_reference',
            'detailed_data', 'generated_at'
        ]
        read_only_fields = [
            'id', 'total_bookings', 'completed_bookings',
            'cancelled_bookings', 'total_ride_value',
            'total_commission_earned', 'average_commission_rate',
            'detailed_data', 'generated_at'
        ]


class BookingQuoteSerializer(serializers.Serializer):
    """Serializer for booking quote requests"""
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    vehicle_type = serializers.ChoiceField(
        choices=['economy', 'comfort', 'luxury', 'van'],
        default='economy'
    )
    passenger_count = serializers.IntegerField(min_value=1, max_value=8, default=1)
    pickup_datetime = serializers.DateTimeField()
    user_tier = serializers.ChoiceField(
        choices=['NORMAL', 'PREMIUM', 'VIP'],
        default='NORMAL'
    )


class BookingQuoteResponseSerializer(serializers.Serializer):
    """Serializer for booking quote responses"""
    estimated_fare = serializers.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = serializers.DurationField()
    distance_km = serializers.DecimalField(max_digits=8, decimal_places=2)
    base_fare = serializers.DecimalField(max_digits=10, decimal_places=2)
    surge_multiplier = serializers.DecimalField(max_digits=5, decimal_places=2)
    hotel_commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    breakdown = serializers.DictField()


class BookingStatusUpdateSerializer(serializers.Serializer):
    """Serializer for booking status updates"""
    booking_reference = serializers.CharField()
    status = serializers.ChoiceField(
        choices=HotelBooking.STATUS_CHOICES
    )
    message = serializers.CharField(max_length=500)
    driver_details = serializers.DictField(required=False)
    estimated_arrival = serializers.DateTimeField(required=False)
    current_location = serializers.DictField(required=False)


class PMSIntegrationLogSerializer(serializers.ModelSerializer):
    """PMS integration log serializer"""
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    
    class Meta:
        model = PMSIntegrationLog
        fields = [
            'id', 'hotel', 'hotel_name', 'action_type', 'success',
            'request_data', 'response_data', 'error_message',
            'booking_reference', 'pms_reference', 'created_at',
            'processing_time'
        ]
        read_only_fields = ['id', 'created_at']
