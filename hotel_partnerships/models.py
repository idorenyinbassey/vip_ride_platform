import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


def validate_vehicle_types(value):
    """Validate that vehicle types list contains only valid types"""
    if not isinstance(value, list):
        raise ValidationError("Value must be a list")
    
    valid_types = ['ECONOMY', 'COMFORT', 'LUXURY', 'VAN']
    for vehicle_type in value:
        if vehicle_type not in valid_types:
            raise ValidationError(f"'{vehicle_type}' is not a valid vehicle type. Valid types: {valid_types}")


class Hotel(models.Model):
    """Hotel partner model with comprehensive details and integration settings"""
    TIER_CHOICES = [
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium'),
        ('LUXURY', 'Luxury'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('PENDING', 'Pending Approval'),
    ]
    
    PMS_TYPES = [
        ('ORACLE_OPERA', 'Oracle Opera'),
        ('FIDELIO', 'Fidelio Suite 8'),
        ('PROTEL', 'Protel Hotel Management'),
        ('CLOUDBEDS', 'CloudBeds'),
        ('MEWS', 'Mews'),
        ('HOTELOGIX', 'Hotelogix'),
        ('CUSTOM', 'Custom System'),
        ('NONE', 'No PMS Integration'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='STANDARD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Location information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Contact information
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Business details
    star_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    total_rooms = models.PositiveIntegerField()
    
    # Partnership terms
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(5.0), MaxValueValidator(25.0)],
        default=Decimal('12.50'),
        help_text="Commission rate percentage (5-25%)"
    )
    minimum_monthly_bookings = models.PositiveIntegerField(default=10)
    preferred_vehicle_types = models.JSONField(
        default=list,
        validators=[validate_vehicle_types],
        help_text="List of preferred vehicle types: ['ECONOMY', 'COMFORT', 'LUXURY', 'VAN']"
    )
    
    # PMS Integration (encrypted sensitive fields)
    pms_type = models.CharField(max_length=20, choices=PMS_TYPES, default='NONE')
    pms_endpoint = models.URLField(blank=True, help_text="PMS API endpoint for integration")
    pms_api_key = models.TextField(blank=True, help_text="Encrypted PMS API key")
    pms_webhook_secret = models.TextField(blank=True, help_text="Encrypted PMS webhook secret")
    
    # Settings
    auto_assign_rides = models.BooleanField(default=True)
    send_real_time_updates = models.BooleanField(default=True)
    allow_bulk_bookings = models.BooleanField(default=True)
    guest_booking_enabled = models.BooleanField(default=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    onboarded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='onboarded_hotels'
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['status', 'tier']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tier})"
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE'
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state}, {self.country}"
    
    def encrypt_pms_credential(self, value):
        """Encrypt PMS credentials for storage"""
        if not value:
            return ""
        
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            import base64
            
            key = base64.urlsafe_b64encode(
                settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            )
            fernet = Fernet(key)
            return fernet.encrypt(value.encode()).decode()
        except Exception:
            # Fallback to storing as-is if encryption fails
            return value
    
    def decrypt_pms_credential(self, encrypted_value):
        """Decrypt PMS credentials for use"""
        if not encrypted_value:
            return ""
        
        try:
            from cryptography.fernet import Fernet
            from django.conf import settings
            import base64
            
            key = base64.urlsafe_b64encode(
                settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            )
            fernet = Fernet(key)
            return fernet.decrypt(encrypted_value.encode()).decode()
        except Exception:
            # Fallback if decryption fails (assume plaintext)
            return encrypted_value
    
    def set_pms_api_key(self, api_key):
        """Set encrypted PMS API key"""
        self.pms_api_key = self.encrypt_pms_credential(api_key)
    
    def get_pms_api_key(self):
        """Get decrypted PMS API key"""
        return self.decrypt_pms_credential(self.pms_api_key)
    
    def set_pms_webhook_secret(self, secret):
        """Set encrypted PMS webhook secret"""
        self.pms_webhook_secret = self.encrypt_pms_credential(secret)
    
    def get_pms_webhook_secret(self):
        """Get decrypted PMS webhook secret"""
        return self.decrypt_pms_credential(self.pms_webhook_secret)


class HotelStaff(models.Model):
    """Hotel staff user accounts with role-based permissions"""
    ROLE_CHOICES = [
        ('ADMIN', 'Hotel Administrator'),
        ('MANAGER', 'General Manager'),
        ('CONCIERGE', 'Concierge'),
        ('FRONT_DESK', 'Front Desk'),
        ('TRANSPORT_COORD', 'Transport Coordinator'),
        ('GUEST_SERVICES', 'Guest Services'),
    ]
    
    PERMISSION_LEVELS = [
        ('FULL', 'Full Access'),
        ('BOOKING_ONLY', 'Booking Only'),
        ('VIEW_ONLY', 'View Only'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hotel_staff')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='staff')
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permission_level = models.CharField(max_length=15, choices=PERMISSION_LEVELS, default='BOOKING_ONLY')
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    
    # Contact details
    phone = models.CharField(max_length=20)
    extension = models.CharField(max_length=10, blank=True)
    
    # Access control
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_hotel_staff'
    )
    
    class Meta:
        unique_together = ['hotel', 'user']
        indexes = [
            models.Index(fields=['hotel', 'is_active']),
            models.Index(fields=['role', 'permission_level']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.hotel.name} ({self.role})"
    
    @property
    def can_make_bookings(self):
        return self.permission_level in ['FULL', 'BOOKING_ONLY'] and self.is_active
    
    @property
    def can_view_analytics(self):
        return self.permission_level == 'FULL' and self.role in ['ADMIN', 'MANAGER']


class HotelRoom(models.Model):
    """Hotel room information for guest booking tracking"""
    ROOM_TYPES = [
        ('STANDARD', 'Standard Room'),
        ('DELUXE', 'Deluxe Room'),
        ('SUITE', 'Suite'),
        ('EXECUTIVE', 'Executive Room'),
        ('PRESIDENTIAL', 'Presidential Suite'),
        ('VILLA', 'Villa'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('OUT_OF_ORDER', 'Out of Order'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    floor = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField(default=2)
    
    # Room features
    amenities = models.JSONField(default=list, help_text="List of room amenities")
    has_balcony = models.BooleanField(default=False)
    has_kitchenette = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='AVAILABLE')
    
    # Pricing (for reference)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hotel', 'room_number']
        ordering = ['hotel', 'floor', 'room_number']
        indexes = [
            models.Index(fields=['hotel', 'status']),
            models.Index(fields=['room_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number}"


class HotelGuest(models.Model):
    """Guest information for tracking bookings and preferences"""
    GUEST_TYPES = [
        ('INDIVIDUAL', 'Individual Guest'),
        ('CORPORATE', 'Corporate Guest'),
        ('GROUP', 'Group Leader'),
        ('VIP', 'VIP Guest'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='guests')
    room = models.ForeignKey(
        HotelRoom, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='current_guests'
    )
    
    # Guest details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    guest_type = models.CharField(max_length=15, choices=GUEST_TYPES, default='INDIVIDUAL')
    
    # Stay information
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField(default=1)
    
    # Preferences
    preferred_vehicle_type = models.CharField(max_length=20, blank=True)
    special_requests = models.TextField(blank=True)
    loyalty_number = models.CharField(max_length=50, blank=True)
    
    # PMS Integration
    pms_guest_id = models.CharField(max_length=100, blank=True, help_text="Guest ID in hotel PMS")
    pms_reservation_id = models.CharField(max_length=100, blank=True)
    
    # Status
    is_checked_in = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-check_in_date']
        indexes = [
            models.Index(fields=['hotel', 'is_checked_in']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['email']),
            models.Index(fields=['pms_guest_id']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.hotel.name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_current_guest(self):
        today = timezone.now().date()
        return self.check_in_date <= today <= self.check_out_date


class HotelBooking(models.Model):
    """Hotel ride bookings with enhanced tracking and commission calculation"""
    BOOKING_TYPES = [
        ('GUEST_REQUEST', 'Guest Request'),
        ('CONCIERGE', 'Concierge Booking'),
        ('FRONT_DESK', 'Front Desk'),
        ('BULK_EVENT', 'Bulk Event'),
        ('AIRPORT_TRANSFER', 'Airport Transfer'),
        ('TOUR', 'Tour/Excursion'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('ASSIGNED', 'Driver Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(
        HotelGuest, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ride_bookings'
    )
    booked_by_staff = models.ForeignKey(
        HotelStaff, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bookings_made'
    )
    
    # Booking details
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES)
    booking_reference = models.CharField(max_length=50, unique=True)
    guest_name = models.CharField(max_length=200, help_text="Guest name if not in system")
    guest_phone = models.CharField(max_length=20)
    guest_room_number = models.CharField(max_length=20, blank=True)
    
    # Trip details
    pickup_location = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    destination = models.TextField()
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Scheduling
    pickup_datetime = models.DateTimeField()
    estimated_duration = models.DurationField(null=True, blank=True)
    
    # Vehicle and service
    vehicle_type = models.CharField(max_length=20, default='ECONOMY')
    passenger_count = models.PositiveIntegerField(default=1)
    special_instructions = models.TextField(blank=True)
    
    # Pricing
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hotel_commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_rate_used = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='NORMAL')
    
    # Integration with ride system
    ride_id = models.UUIDField(null=True, blank=True, help_text="Reference to main ride booking")
    driver_assigned = models.JSONField(null=True, blank=True, help_text="Driver details")
    
    # Tracking and updates
    status_updates = models.JSONField(default=list, help_text="Status update history")
    last_update_sent = models.DateTimeField(null=True, blank=True)
    
    # Event booking specific
    event_name = models.CharField(max_length=200, blank=True)
    bulk_booking_group = models.UUIDField(null=True, blank=True, help_text="Groups bulk bookings")
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-pickup_datetime']
        indexes = [
            models.Index(fields=['hotel', 'status']),
            models.Index(fields=['pickup_datetime']),
            models.Index(fields=['booking_reference']),
            models.Index(fields=['guest', 'status']),
            models.Index(fields=['bulk_booking_group']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.booking_reference} - {self.hotel.name}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        """Generate unique booking reference with collision prevention"""
        import random
        import string
        
        max_attempts = 10
        for attempt in range(max_attempts):
            timestamp = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            reference = f"HTL{timestamp}{random_str}"
            
            # Check if reference already exists
            if not HotelBooking.objects.filter(booking_reference=reference).exists():
                return reference
        
        # If all attempts failed, add a longer random suffix
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"HTL{timestamp}{random_str}"
    
    def calculate_commission(self):
        """Calculate hotel commission based on final fare"""
        if self.final_fare and self.hotel.commission_rate:
            commission = self.final_fare * (self.hotel.commission_rate / Decimal('100'))
            self.hotel_commission = commission
            self.commission_rate_used = self.hotel.commission_rate
            return commission
        return Decimal('0.00')
    
    def add_status_update(self, status, message, user=None):
        """Add status update to tracking history with size limit"""
        update = {
            'timestamp': timezone.now().isoformat(),
            'status': status,
            'message': message,
            'user': user.username if user else 'system'
        }
        if not self.status_updates:
            self.status_updates = []
        
        self.status_updates.append(update)
        
        # Keep only the most recent 50 updates to prevent unbounded growth
        if len(self.status_updates) > 50:
            self.status_updates = self.status_updates[-50:]
        
        self.status = status
        self.save()


class HotelCommissionReport(models.Model):
    """Monthly commission reports for hotels"""
    REPORT_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
        ('DISPUTED', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='commission_reports')
    
    # Report period
    report_month = models.DateField(help_text="First day of the month being reported")
    
    # Metrics
    total_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    
    # Financial
    total_ride_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Performance
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    response_time_avg = models.DurationField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=15, choices=REPORT_STATUS, default='PENDING')
    
    # Payment details
    payment_due_date = models.DateField(null=True, blank=True)
    payment_made_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Report data
    detailed_data = models.JSONField(default=dict, help_text="Detailed breakdown of bookings")
    
    # Audit
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='generated_commission_reports'
    )
    
    class Meta:
        unique_together = ['hotel', 'report_month']
        ordering = ['-report_month']
        indexes = [
            models.Index(fields=['hotel', 'status']),
            models.Index(fields=['report_month']),
            models.Index(fields=['status', 'payment_due_date']),
        ]
    
    def __str__(self):
        return f"{self.hotel.name} - {self.report_month.strftime('%B %Y')}"


class BulkBookingEvent(models.Model):
    """Bulk booking events for conferences, weddings, etc."""
    EVENT_TYPES = [
        ('CONFERENCE', 'Conference'),
        ('WEDDING', 'Wedding'),
        ('CORPORATE', 'Corporate Event'),
        ('SPORTS', 'Sports Event'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('EXHIBITION', 'Exhibition'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bulk_events')
    
    # Event details
    event_name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES)
    description = models.TextField(blank=True)
    
    # Scheduling
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Logistics
    expected_guests = models.PositiveIntegerField()
    pickup_locations = models.JSONField(default=list, help_text="List of pickup locations")
    destination_venue = models.TextField()
    
    # Service requirements
    vehicle_types_needed = models.JSONField(default=list)
    estimated_rides = models.PositiveIntegerField()
    special_requirements = models.TextField(blank=True)
    
    # Coordination
    event_coordinator_name = models.CharField(max_length=200)
    event_coordinator_phone = models.CharField(max_length=20)
    event_coordinator_email = models.EmailField()
    
    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PLANNING')
    
    # Pricing
    estimated_total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        HotelStaff, on_delete=models.SET_NULL, null=True,
        related_name='created_bulk_events'
    )
    
    class Meta:
        ordering = ['-event_date']
        indexes = [
            models.Index(fields=['hotel', 'status']),
            models.Index(fields=['event_date']),
            models.Index(fields=['event_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.hotel.name}"


class PMSIntegrationLog(models.Model):
    """Log PMS integration activities and errors"""
    ACTION_TYPES = [
        ('GUEST_SYNC', 'Guest Data Sync'),
        ('BOOKING_CREATE', 'Booking Creation'),
        ('STATUS_UPDATE', 'Status Update'),
        ('COMMISSION_SYNC', 'Commission Sync'),
        ('WEBHOOK_RECEIVED', 'Webhook Received'),
        ('ERROR', 'Error Occurred'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='pms_logs')
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    success = models.BooleanField(default=True)
    
    # Request/Response data
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Related objects
    booking_reference = models.CharField(max_length=50, blank=True)
    pms_reference = models.CharField(max_length=100, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hotel', 'action_type']),
            models.Index(fields=['success', 'created_at']),
            models.Index(fields=['booking_reference']),
        ]
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.action_type} - {self.hotel.name}"
