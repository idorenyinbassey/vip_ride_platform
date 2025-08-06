# Serializers for Ride Matching System
"""
Django REST Framework serializers for ride matching functionality
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from decimal import Decimal

from .models import Ride, RideStatus, RideType
from .models import (
    RideOffer, SurgeZone, RideMatchingLog, DriverPreference, CustomerPreference
)
from accounts.models import Driver


class RideOfferSerializer(serializers.ModelSerializer):
    """Serializer for ride offers"""
    
    driver_name = serializers.CharField(
        source='driver.get_full_name', read_only=True
    )
    driver_rating = serializers.DecimalField(
        source='driver.driver_profile.average_rating',
        max_digits=3, decimal_places=2, read_only=True
    )
    vehicle_info = serializers.SerializerMethodField()
    time_remaining_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = RideOffer
        fields = [
            'id', 'ride', 'driver', 'driver_name', 'driver_rating',
            'estimated_arrival_time', 'driver_latitude', 'driver_longitude',
            'status', 'created_at', 'expires_at', 'responded_at',
            'surge_multiplier_at_offer', 'vehicle_info', 'time_remaining_minutes'
        ]
        read_only_fields = [
            'id', 'created_at', 'driver_name', 'driver_rating',
            'vehicle_info', 'time_remaining_minutes'
        ]
    
    def get_vehicle_info(self, obj):
        """Get vehicle information for the offer"""
        try:
            driver = Driver.objects.get(user=obj.driver)
            # Get driver's primary vehicle
            if hasattr(driver, 'assigned_vehicles'):
                vehicle = driver.assigned_vehicles.filter(
                    status='active'
                ).first()
            else:
                from fleet_management.models import Vehicle
                vehicle = Vehicle.objects.filter(
                    owner=obj.driver,
                    status='active'
                ).first()
            
            if vehicle:
                return {
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'color': vehicle.color,
                    'license_plate': vehicle.license_plate,
                    'category': vehicle.category
                }
        except (Driver.DoesNotExist, AttributeError):
            pass
        
        return None
    
    def get_time_remaining_minutes(self, obj):
        """Calculate remaining time for offer"""
        from django.utils import timezone
        
        if obj.status != RideOffer.OfferStatus.PENDING:
            return 0
        
        remaining = obj.expires_at - timezone.now()
        return max(0, int(remaining.total_seconds() / 60))


class RideSerializer(serializers.ModelSerializer):
    """Serializer for rides with matching information"""
    
    customer_name = serializers.CharField(
        source='customer.get_full_name', read_only=True
    )
    driver_name = serializers.CharField(
        source='driver.get_full_name', read_only=True
    )
    offers_count = serializers.SerializerMethodField()
    active_offers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Ride
        fields = [
            'id', 'customer', 'customer_name', 'customer_tier',
            'driver', 'driver_name', 'ride_type', 'status',
            'pickup_address', 'pickup_latitude', 'pickup_longitude',
            'destination_address', 'destination_latitude', 'destination_longitude',
            'requested_at', 'accepted_at', 'started_at', 'completed_at',
            'surge_multiplier', 'base_fare', 'total_fare',
            'requires_baby_seat', 'requires_wheelchair_access',
            'requires_premium_vehicle', 'preferred_driver',
            'offers_count', 'active_offers_count'
        ]
        read_only_fields = [
            'id', 'customer_name', 'driver_name', 'surge_multiplier',
            'offers_count', 'active_offers_count'
        ]
    
    def get_offers_count(self, obj):
        """Get total number of offers for this ride"""
        return obj.offers.count()
    
    def get_active_offers_count(self, obj):
        """Get number of active offers for this ride"""
        from django.utils import timezone
        return obj.offers.filter(
            status=RideOffer.OfferStatus.PENDING,
            expires_at__gt=timezone.now()
        ).count()


class SurgeZoneSerializer(serializers.ModelSerializer):
    """Serializer for surge zones"""
    
    is_currently_active = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True
    )
    
    class Meta:
        model = SurgeZone
        fields = [
            'id', 'name', 'center_latitude', 'center_longitude',
            'radius_km', 'surge_multiplier', 'is_active',
            'active_from', 'active_until', 'min_demand_ratio',
            'min_ride_requests', 'is_currently_active',
            'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'is_currently_active', 'created_at',
            'created_by_name'
        ]


class RideMatchingLogSerializer(serializers.ModelSerializer):
    """Serializer for ride matching logs"""
    
    ride_info = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = RideMatchingLog
        fields = [
            'id', 'ride', 'timestamp', 'search_radius_km',
            'drivers_in_radius', 'drivers_eligible', 'drivers_contacted',
            'offers_created', 'match_successful', 'match_duration_seconds',
            'surge_multiplier', 'surge_zone', 'customer_tier',
            'ride_type', 'ride_info', 'success_rate'
        ]
        read_only_fields = ['id', 'ride_info', 'success_rate']
    
    def get_ride_info(self, obj):
        """Get basic ride information"""
        return {
            'ride_id': str(obj.ride.id),
            'customer_name': obj.ride.customer.get_full_name(),
            'pickup_address': obj.ride.pickup_address,
            'status': obj.ride.status
        }
    
    def get_success_rate(self, obj):
        """Calculate success rate for this matching attempt"""
        if obj.drivers_contacted == 0:
            return 0
        return (obj.offers_created / obj.drivers_contacted) * 100


class DriverPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for driver preferences"""
    
    driver_name = serializers.CharField(
        source='driver.user.get_full_name', read_only=True
    )
    
    class Meta:
        model = DriverPreference
        fields = [
            'id', 'driver', 'driver_name', 'preferred_pickup_areas',
            'avoided_areas', 'max_pickup_distance_km', 'accepts_airport_rides',
            'accepts_long_distance', 'accepts_night_rides',
            'min_ride_duration_minutes', 'vip_customers_only',
            'familiar_customers_priority', 'working_hours_start',
            'working_hours_end', 'working_days', 'updated_at'
        ]
        read_only_fields = ['id', 'driver_name', 'updated_at']


class CustomerPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for customer preferences"""
    
    customer_name = serializers.CharField(
        source='customer.get_full_name', read_only=True
    )
    preferred_drivers_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerPreference
        fields = [
            'id', 'customer', 'customer_name', 'preferred_drivers',
            'preferred_drivers_info', 'blocked_drivers',
            'preferred_vehicle_types', 'requires_non_smoking',
            'requires_air_conditioning', 'max_waiting_time_minutes',
            'accepts_shared_rides', 'price_sensitivity',
            'requires_baby_seat', 'requires_wheelchair_access',
            'has_pet', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_name', 'preferred_drivers_info', 'updated_at'
        ]
    
    def get_preferred_drivers_info(self, obj):
        """Get information about preferred drivers"""
        return [
            {
                'id': driver.id,
                'name': driver.user.get_full_name(),
                'rating': float(driver.average_rating or 0),
                'subscription_tier': driver.subscription_tier
            }
            for driver in obj.preferred_drivers.all()
        ]


class RideMatchingStatsSerializer(serializers.Serializer):
    """Serializer for ride matching statistics"""
    
    total_rides_requested = serializers.IntegerField()
    successful_matches = serializers.IntegerField()
    no_driver_found = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_matching_time = serializers.DurationField()
    surge_zones_active = serializers.IntegerField()
    
    # Additional stats
    tier_breakdown = serializers.DictField(child=serializers.IntegerField(), required=False)
    hourly_breakdown = serializers.DictField(child=serializers.IntegerField(), required=False)
    driver_utilization = serializers.FloatField(required=False)


class DriverLocationSerializer(serializers.Serializer):
    """Serializer for driver location updates"""
    
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    accuracy_meters = serializers.IntegerField(required=False)
    is_available = serializers.BooleanField(required=False)
    
    def validate_latitude(self, value):
        """Validate latitude range"""
        if not (-90 <= value <= 90):
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90"
            )
        return value
    
    def validate_longitude(self, value):
        """Validate longitude range"""
        if not (-180 <= value <= 180):
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180"
            )
        return value


class RideRequestSerializer(serializers.Serializer):
    """Serializer for ride requests"""
    
    ride_type = serializers.ChoiceField(choices=RideType.choices)
    pickup_address = serializers.CharField(max_length=255)
    pickup_latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    pickup_longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    destination_address = serializers.CharField(max_length=255)
    destination_latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    destination_longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    
    # Special requirements
    requires_baby_seat = serializers.BooleanField(default=False)
    requires_wheelchair_access = serializers.BooleanField(default=False)
    requires_premium_vehicle = serializers.BooleanField(default=False)
    
    # Preferences
    preferred_driver_id = serializers.UUIDField(required=False)
    max_waiting_time_minutes = serializers.IntegerField(default=10)
    
    # Additional info
    passenger_count = serializers.IntegerField(default=1, min_value=1, max_value=8)
    special_instructions = serializers.CharField(max_length=500, required=False)
    
    def validate_passenger_count(self, value):
        """Validate passenger count"""
        if value < 1:
            raise serializers.ValidationError(
                "At least 1 passenger is required"
            )
        return value
    
    def validate_preferred_driver_id(self, value):
        """Validate preferred driver exists and is available"""
        if value:
            try:
                driver = Driver.objects.get(user_id=value, is_active=True)
                if not driver.is_online or not driver.is_available:
                    raise serializers.ValidationError(
                        "Preferred driver is not currently available"
                    )
            except Driver.DoesNotExist:
                raise serializers.ValidationError(
                    "Preferred driver not found"
                )
        return value


class DriverResponseSerializer(serializers.Serializer):
    """Serializer for driver responses to ride offers"""
    
    offer_id = serializers.UUIDField()
    accepted = serializers.BooleanField()
    estimated_arrival_minutes = serializers.IntegerField(
        required=False, min_value=1, max_value=60
    )
    current_latitude = serializers.DecimalField(
        max_digits=10, decimal_places=7, required=False
    )
    current_longitude = serializers.DecimalField(
        max_digits=10, decimal_places=7, required=False
    )
    
    def validate_offer_id(self, value):
        """Validate offer exists and is pending"""
        try:
            offer = RideOffer.objects.get(id=value)
            if offer.status != RideOffer.OfferStatus.PENDING:
                raise serializers.ValidationError(
                    "Offer is no longer pending"
                )
            if offer.is_expired:
                raise serializers.ValidationError(
                    "Offer has expired"
                )
        except RideOffer.DoesNotExist:
            raise serializers.ValidationError(
                "Offer not found"
            )
        return value
