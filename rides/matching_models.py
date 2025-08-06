# Extended Ride Models for Matching Algorithm
"""
Additional models and fields needed for the ride matching system
Note: RideOffer model already exists in rides/models.py so we don't redefine it here
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal


# Add these fields to existing Ride model
class RideExtension:
    """
    Fields to add to existing Ride model for matching algorithm
    These would be added as a migration to the existing Ride model
    """
    
    # Surge pricing
    surge_multiplier = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('1.00'),
        help_text="Surge pricing multiplier applied to this ride"
    )
    
    # Special requirements
    requires_baby_seat = models.BooleanField(default=False)
    requires_wheelchair_access = models.BooleanField(default=False)
    requires_premium_vehicle = models.BooleanField(default=False)
    
    # Matching metadata
    matching_started_at = models.DateTimeField(null=True, blank=True)
    matching_completed_at = models.DateTimeField(null=True, blank=True)
    drivers_contacted = models.IntegerField(default=0)
    
    # Customer preferences for VIP
    preferred_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='preferred_rides'
    )
    
    # Location accuracy for better matching
    pickup_accuracy_meters = models.IntegerField(null=True, blank=True)
    destination_accuracy_meters = models.IntegerField(null=True, blank=True)


# Additional status choices for existing Ride model
class RideStatusExtension:
    """Additional status choices for Ride model"""
    
    NO_DRIVER_FOUND = 'no_driver_found', 'No Driver Found'
    DRIVER_ARRIVING = 'driver_arriving', 'Driver Arriving'
    DRIVER_ARRIVED = 'driver_arrived', 'Driver Arrived'


class DriverLocationHistory(models.Model):
    """Track driver location history for analytics and optimization"""
    
    driver = models.ForeignKey('accounts.Driver', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField(auto_now_add=True)
    accuracy_meters = models.IntegerField(null=True, blank=True)
    
    # Context
    is_available = models.BooleanField(default=False)
    is_on_ride = models.BooleanField(default=False)
    current_ride = models.ForeignKey(
        'Ride', on_delete=models.SET_NULL, null=True, blank=True
    )
    
    class Meta:
        db_table = 'driver_location_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['driver', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_available', 'timestamp']),
        ]


class SurgeZone(models.Model):
    """Model for managing surge pricing zones"""
    
    name = models.CharField(max_length=100)
    center_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    center_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    radius_km = models.FloatField()
    
    # Surge settings
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2)
    is_active = models.BooleanField(default=True)
    active_from = models.DateTimeField()
    active_until = models.DateTimeField()
    
    # Trigger conditions
    min_demand_ratio = models.FloatField(default=1.5, help_text="Demand/supply ratio to activate")
    min_ride_requests = models.IntegerField(default=10, help_text="Minimum rides in timeframe")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    
    class Meta:
        db_table = 'surge_zones'
        ordering = ['-created_at']
    
    @property
    def is_currently_active(self):
        """Check if surge zone is currently active"""
        now = timezone.now()
        return (
            self.is_active and 
            self.active_from <= now <= self.active_until
        )
    
    def __str__(self):
        return f"{self.name} - {self.surge_multiplier}x surge"


class RideMatchingLog(models.Model):
    """Log ride matching attempts for analytics and debugging"""
    
    ride = models.ForeignKey('Ride', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Search parameters
    search_radius_km = models.FloatField()
    drivers_in_radius = models.IntegerField()
    drivers_eligible = models.IntegerField()
    drivers_contacted = models.IntegerField()
    
    # Results
    offers_created = models.IntegerField()
    match_successful = models.BooleanField()
    match_duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Surge info
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2)
    surge_zone = models.ForeignKey(
        SurgeZone, on_delete=models.SET_NULL, null=True, blank=True
    )
    
    # Additional context
    customer_tier = models.CharField(max_length=20)
    ride_type = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'ride_matching_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['match_successful', 'timestamp']),
        ]


class DriverPreference(models.Model):
    """Driver preferences for ride matching"""
    
    driver = models.OneToOneField(
        'accounts.Driver', on_delete=models.CASCADE, related_name='matching_preferences'
    )
    
    # Geographic preferences
    preferred_pickup_areas = models.JSONField(
        default=list, help_text="List of preferred pickup area coordinates"
    )
    avoided_areas = models.JSONField(
        default=list, help_text="List of areas driver prefers to avoid"
    )
    max_pickup_distance_km = models.FloatField(default=15.0)
    
    # Ride type preferences
    accepts_airport_rides = models.BooleanField(default=True)
    accepts_long_distance = models.BooleanField(default=True)
    accepts_night_rides = models.BooleanField(default=True)
    min_ride_duration_minutes = models.IntegerField(default=5)
    
    # Customer preferences
    vip_customers_only = models.BooleanField(default=False)
    familiar_customers_priority = models.BooleanField(default=True)
    
    # Schedule preferences
    working_hours_start = models.TimeField(null=True, blank=True)
    working_hours_end = models.TimeField(null=True, blank=True)
    working_days = models.JSONField(
        default=list, help_text="List of working days (0=Monday, 6=Sunday)"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'driver_preferences'


class CustomerPreference(models.Model):
    """Customer preferences for ride matching"""
    
    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name='ride_preferences'
    )
    
    # Driver preferences
    preferred_drivers = models.ManyToManyField(
        'accounts.Driver', blank=True, related_name='preferred_by_customers'
    )
    blocked_drivers = models.ManyToManyField(
        'accounts.Driver', blank=True, related_name='blocked_by_customers'
    )
    
    # Vehicle preferences
    preferred_vehicle_types = models.JSONField(default=list)
    requires_non_smoking = models.BooleanField(default=False)
    requires_air_conditioning = models.BooleanField(default=False)
    
    # Service preferences
    max_waiting_time_minutes = models.IntegerField(default=10)
    accepts_shared_rides = models.BooleanField(default=False)
    price_sensitivity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Price Sensitive'),
            ('medium', 'Balanced'),
            ('high', 'Service Priority')
        ],
        default='medium'
    )
    
    # Special needs
    requires_baby_seat = models.BooleanField(default=False)
    requires_wheelchair_access = models.BooleanField(default=False)
    has_pet = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_preferences'
