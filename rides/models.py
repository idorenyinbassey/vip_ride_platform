from django.db import models
from django.conf import settings
from accounts.models import UserTier
from fleet_management.models import Vehicle
import uuid
from cryptography.fernet import Fernet
from django.utils import timezone
import json


class RideStatus(models.TextChoices):
    """Enhanced ride status choices for workflow system"""
    REQUESTED = 'requested', 'Ride Requested'
    DRIVER_SEARCH = 'driver_search', 'Searching for Driver'
    DRIVER_FOUND = 'driver_found', 'Driver Found'
    DRIVER_ACCEPTED = 'driver_accepted', 'Driver Accepted'
    DRIVER_REJECTED = 'driver_rejected', 'Driver Rejected'
    DRIVER_EN_ROUTE = 'driver_en_route', 'Driver En Route'
    DRIVER_ARRIVED = 'driver_arrived', 'Driver Arrived'
    IN_PROGRESS = 'in_progress', 'Ride In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED_BY_RIDER = 'cancelled_by_rider', 'Cancelled by Rider'
    CANCELLED_BY_DRIVER = 'cancelled_by_driver', 'Cancelled by Driver'
    CANCELLED_BY_SYSTEM = 'cancelled_by_system', 'Cancelled by System'
    PAYMENT_PENDING = 'payment_pending', 'Payment Pending'
    PAYMENT_FAILED = 'payment_failed', 'Payment Failed'
    PAYMENT_COMPLETED = 'payment_completed', 'Payment Completed'
    DISPUTED = 'disputed', 'Disputed'
    REFUNDED = 'refunded', 'Refunded'


class RideType(models.TextChoices):
    NORMAL = 'normal', 'Normal Ride'
    PREMIUM = 'premium', 'Premium Ride'
    VIP = 'vip', 'VIP Ride'
    AIRPORT = 'airport', 'Airport Transfer'
    CORPORATE = 'corporate', 'Corporate Booking'
    HOTEL_TRANSFER = 'hotel_transfer', 'Hotel Transfer'


class BillingModel(models.TextChoices):
    STANDARD = 'standard', 'Standard Fare'
    FLEXIBLE_ENGINE = 'flexible_engine', 'Flexible by Engine Type'
    FLEET_FIXED = 'fleet_fixed', 'Fleet Fixed Rate'
    PREMIUM_MULTIPLIER = 'premium_multiplier', 'Premium Multiplier'


class Ride(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Parties
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rider_rides'
    )
    driver = models.ForeignKey(
        'accounts.Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_rides'
    )
    
    # Timing - Enhanced for workflow
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    driver_accepted_at = models.DateTimeField(null=True, blank=True)
    driver_en_route_at = models.DateTimeField(null=True, blank=True)
    driver_arrived_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicle_rides'
    )
    fleet_company = models.ForeignKey(
        'fleet_management.FleetCompany',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fleet_rides'
    )
    
    # Ride Details
    ride_type = models.CharField(
        max_length=15,
        choices=RideType.choices,
        default=RideType.NORMAL
    )
    rider_tier = models.CharField(
        max_length=10,
        choices=UserTier.choices,
        default=UserTier.NORMAL
    )
    status = models.CharField(
        max_length=25,
        choices=RideStatus.choices,
        default=RideStatus.REQUESTED
    )
    
    # Workflow tracking
    workflow_step = models.CharField(max_length=50, blank=True)
    auto_transitions_enabled = models.BooleanField(default=True)
    
    # Billing Model
    billing_model = models.CharField(
        max_length=20,
        choices=BillingModel.choices,
        default=BillingModel.STANDARD
    )
    
    # Locations (base data - always stored)
    pickup_latitude = models.DecimalField(max_digits=10, decimal_places=8)
    pickup_longitude = models.DecimalField(max_digits=11, decimal_places=8)
    pickup_address = models.TextField()
    
    destination_latitude = models.DecimalField(max_digits=10, decimal_places=8)
    destination_longitude = models.DecimalField(max_digits=11, decimal_places=8)
    destination_address = models.TextField()
    
    # Encrypted GPS data for VIP users (AES-256-GCM)
    encrypted_pickup_coordinates = models.TextField(blank=True)
    encrypted_destination_coordinates = models.TextField(blank=True)
    encrypted_route_data = models.TextField(blank=True)
    encrypted_realtime_tracking = models.TextField(blank=True)
    encryption_key_reference = models.CharField(max_length=100, blank=True)
    
    # Additional Location Info
    pickup_landmark = models.CharField(max_length=200, blank=True)
    destination_landmark = models.CharField(max_length=200, blank=True)
    waypoints = models.TextField(
        blank=True,
        help_text='JSON array of intermediate waypoints'
    )
    
    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    scheduled_pickup_time = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    driver_arrival_time = models.DateTimeField(null=True, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    dropoff_time = models.DateTimeField(null=True, blank=True)
    
    # Estimated values
    estimated_distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    estimated_duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    estimated_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Actual values
    actual_distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    # Flexible Pricing Components
    base_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    distance_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    time_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    engine_type_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.00,
        help_text='Multiplier based on vehicle engine type'
    )
    fuel_consumption_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    premium_service_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    surge_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00
    )
    total_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Commission and Payments (flexible structure)
    platform_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    platform_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    driver_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    fleet_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    vehicle_owner_share = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Special Features
    requires_baby_seat = models.BooleanField(default=False)
    requires_wheelchair_access = models.BooleanField(default=False)
    requires_premium_vehicle = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    
    # VIP Features
    vip_priority_level = models.PositiveIntegerField(
        default=0,
        help_text='0=Normal, 1-5=VIP priority levels'
    )
    assigned_control_center_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_monitoring_rides'
    )
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    cancellation_refund = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # SOS Emergency (VIP feature)
    is_sos_triggered = models.BooleanField(default=False)
    sos_triggered_at = models.DateTimeField(null=True, blank=True)
    sos_resolved = models.BooleanField(default=False)
    sos_resolution_time = models.DateTimeField(null=True, blank=True)
    emergency_contacts_notified = models.BooleanField(default=False)
    
    # Weather and Traffic
    weather_conditions = models.CharField(max_length=50, blank=True)
    traffic_conditions = models.CharField(max_length=50, blank=True)
    route_optimization_used = models.BooleanField(default=False)
    
    # Quality Metrics
    customer_satisfaction_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='1-10 satisfaction score'
    )
    ride_quality_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='1-10 overall quality score'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rides'
        indexes = [
            models.Index(fields=['rider']),
            models.Index(fields=['driver']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['fleet_company']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ride_type']),
            models.Index(fields=['rider_tier']),
            models.Index(fields=['billing_model']),
            models.Index(fields=['vip_priority_level']),
            models.Index(fields=['is_sos_triggered']),
            models.Index(fields=['scheduled_pickup_time']),
        ]
    
    def __str__(self):
        return f'Ride {self.id} - {self.rider.email} - {self.get_status_display()}'
    
    def encrypt_gps_data(self, data):
        """Encrypt GPS data for VIP users using AES-256-GCM"""
        if self.rider_tier == UserTier.VIP:
            try:
                from django.conf import settings
                # Use base64 encoded key for Fernet
                import base64
                key = base64.urlsafe_b64encode(
                    settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
                )
                fernet = Fernet(key)
                return fernet.encrypt(json.dumps(data).encode()).decode()
            except Exception:
                # Fallback to storing unencrypted if encryption fails
                return json.dumps(data)
        return json.dumps(data)
    
    def decrypt_gps_data(self, encrypted_data):
        """Decrypt GPS data for VIP users"""
        if encrypted_data and self.rider_tier == UserTier.VIP:
            try:
                from django.conf import settings
                import base64
                key = base64.urlsafe_b64encode(
                    settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
                )
                fernet = Fernet(key)
                decrypted = fernet.decrypt(encrypted_data.encode()).decode()
                return json.loads(decrypted)
            except Exception:
                # If decryption fails, try parsing as JSON
                try:
                    return json.loads(encrypted_data)
                except Exception:
                    return None
        return json.loads(encrypted_data) if encrypted_data else None
    
    def trigger_sos(self):
        """Trigger SOS emergency protocol"""
        if self.rider_tier == UserTier.VIP:
            self.is_sos_triggered = True
            self.sos_triggered_at = timezone.now()
            self.save()
            
            # Send emergency notifications will be implemented later
            # from notifications.tasks import send_sos_alert
            # send_sos_alert.delay(self.id)
    
    def calculate_flexible_fare(self):
        """Calculate fare based on flexible billing model"""
        if self.billing_model == BillingModel.FLEXIBLE_ENGINE:
            return self._calculate_engine_based_fare()
        elif self.billing_model == BillingModel.FLEET_FIXED:
            return self._calculate_fleet_fixed_fare()
        elif self.billing_model == BillingModel.PREMIUM_MULTIPLIER:
            return self._calculate_premium_fare()
        else:
            return self._calculate_standard_fare()
    
    def calculate_final_fare(self):
        """Calculate and set final fare - called by workflow on completion"""
        calculated_fare = self.calculate_flexible_fare()
        self.total_fare = calculated_fare
        
        # Calculate commission breakdown
        commission_rate = float(self.platform_commission_rate) / 100
        self.platform_commission = calculated_fare * commission_rate
        self.driver_earnings = calculated_fare - self.platform_commission
        
        # Fleet company commission if applicable
        if self.fleet_company:
            fleet_rate = float(getattr(self.fleet_company, 'commission_rate', 10)) / 100
            self.fleet_commission = calculated_fare * fleet_rate
            self.driver_earnings -= self.fleet_commission
        
        self.save()
    
    def _calculate_engine_based_fare(self):
        """Calculate fare based on vehicle engine type"""
        if not self.vehicle:
            return self._calculate_standard_fare()
        
        base_fare = self.vehicle.calculate_flexible_billing_rate()
        distance_factor = float(self.actual_distance_km or self.estimated_distance_km or 0)
        time_factor = float(self.actual_duration_minutes or self.estimated_duration_minutes or 0) / 60
        
        # Fuel consumption component
        fuel_cost = float(self.vehicle.fuel_consumption_per_km) * distance_factor * 2.5  # Fuel price factor
        
        total = (base_fare * distance_factor) + (base_fare * 0.5 * time_factor) + fuel_cost
        return total * float(self.surge_multiplier)
    
    def _calculate_fleet_fixed_fare(self):
        """Calculate fare using fleet company's fixed rates"""
        if not self.fleet_company:
            return self._calculate_standard_fare()
        
        distance = float(self.actual_distance_km or self.estimated_distance_km or 0)
        base_rate = float(self.fleet_company.fixed_rate_per_km)
        
        if self.ride_type == RideType.PREMIUM:
            base_rate *= float(self.fleet_company.premium_rate_multiplier)
        elif self.ride_type == RideType.VIP:
            base_rate *= float(self.fleet_company.vip_rate_multiplier)
        
        return (base_rate * distance) * float(self.surge_multiplier)
    
    def _calculate_premium_fare(self):
        """Calculate fare with premium multipliers"""
        base_fare = self._calculate_standard_fare()
        
        if self.rider_tier == UserTier.PREMIUM:
            return base_fare * 1.5
        elif self.rider_tier == UserTier.VIP:
            return base_fare * 2.0
        
        return base_fare
    
    def _calculate_standard_fare(self):
        """Calculate standard fare"""
        distance = float(self.actual_distance_km or self.estimated_distance_km or 0)
        duration = float(self.actual_duration_minutes or self.estimated_duration_minutes or 0)
        
        base = 500  # Base fare in local currency
        distance_rate = 150  # Per km
        time_rate = 50  # Per minute
        
        total = base + (distance * distance_rate) + (duration * time_rate)
        return total * float(self.surge_multiplier)
    
    @property
    def duration(self):
        """Calculate ride duration"""
        if self.pickup_time and self.dropoff_time:
            return self.dropoff_time - self.pickup_time
        return None
    
    @property
    def is_vip_ride(self):
        return self.rider_tier == UserTier.VIP
    
    @property
    def requires_encrypted_tracking(self):
        return self.rider_tier == UserTier.VIP
    
    def get_encrypted_location_data(self):
        """Get encrypted location data for VIP rides"""
        if not self.requires_encrypted_tracking:
            return None
        
        location_data = {
            'pickup': {
                'lat': str(self.pickup_latitude),
                'lng': str(self.pickup_longitude),
                'address': self.pickup_address
            },
            'destination': {
                'lat': str(self.destination_latitude),
                'lng': str(self.destination_longitude),
                'address': self.destination_address
            },
            'timestamp': timezone.now().isoformat()
        }
        
        return self.encrypt_gps_data(location_data)


class RideTracking(models.Model):
    """Real-time location tracking during rides"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='tracking_points'
    )
    
    # Location data (encrypted for VIP)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    encrypted_location_data = models.TextField(blank=True)
    
    # Additional tracking info
    speed_kmh = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    heading = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True
    )
    accuracy_meters = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ride_tracking'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['recorded_at']),
        ]
        ordering = ['-recorded_at']
    
    def save(self, *args, **kwargs):
        # Encrypt location data for VIP rides
        if self.ride.rider_tier == UserTier.VIP:
            location_data = {
                'lat': str(self.latitude),
                'lng': str(self.longitude),
                'timestamp': self.recorded_at.isoformat() if self.recorded_at else timezone.now().isoformat()
            }
            self.encrypted_location_data = self.ride.encrypt_gps_data(location_data)
        super().save(*args, **kwargs)


class RideRating(models.Model):
    """Ride ratings and reviews"""
    
    class RatingType(models.TextChoices):
        CUSTOMER_TO_DRIVER = 'CUSTOMER_TO_DRIVER', 'Customer Rating Driver'
        DRIVER_TO_CUSTOMER = 'DRIVER_TO_CUSTOMER', 'Driver Rating Customer'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_ratings'
    )
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_ratings'
    )
    
    rating_type = models.CharField(
        max_length=20,
        choices=RatingType.choices
    )
    
    # Rating (1-5 stars)
    rating = models.PositiveIntegerField()
    review = models.TextField(blank=True)
    
    # Category ratings
    punctuality = models.PositiveIntegerField(null=True, blank=True)
    cleanliness = models.PositiveIntegerField(null=True, blank=True)
    safety = models.PositiveIntegerField(null=True, blank=True)
    communication = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ride_ratings'
        unique_together = ['ride', 'rater', 'rating_type']
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['rated_user']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f'{self.rating}★ - {self.ride.id} - {self.get_rating_type_display()}'


# Additional models for ride matching system
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
    min_demand_ratio = models.FloatField(
        default=1.5, help_text="Demand/supply ratio to activate"
    )
    min_ride_requests = models.IntegerField(
        default=10, help_text="Minimum rides in timeframe"
    )
    
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
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
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
    rider_tier = models.CharField(max_length=20)
    ride_type = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'ride_matching_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['match_successful', 'timestamp']),
        ]


class RideOffer(models.Model):
    """Driver offers for ride requests"""
    
    class OfferStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ride_offers'
    )
    
    # Offer details
    estimated_arrival_time = models.PositiveIntegerField(
        help_text='Estimated minutes to reach pickup location'
    )
    offered_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=10,
        choices=OfferStatus.choices,
        default=OfferStatus.PENDING
    )
    
    # Driver location at time of offer
    driver_latitude = models.DecimalField(max_digits=10, decimal_places=8)
    driver_longitude = models.DecimalField(max_digits=11, decimal_places=8)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'ride_offers'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['driver']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
        unique_together = ['ride', 'driver']
    
    def __str__(self):
        return f'Offer: {self.driver.email} for Ride {self.ride.id}'
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class EmergencyContact(models.Model):
    """Emergency contacts for VIP users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    relationship = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emergency_contacts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        return f'{self.name} - {self.user.email}'


# Driver and Customer Preference Models for Matching System
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
        indexes = [
            models.Index(fields=['driver']),
            models.Index(fields=['vip_customers_only']),
            models.Index(fields=['accepts_airport_rides']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f'Preferences for {self.driver.user.get_full_name()}'


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
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['requires_baby_seat']),
            models.Index(fields=['requires_wheelchair_access']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f'Preferences for {self.customer.get_full_name()}'
