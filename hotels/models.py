from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from decimal import Decimal


class HotelCategory(models.TextChoices):
    BUDGET = 'budget', 'Budget Hotel'
    STANDARD = 'standard', 'Standard Hotel'
    LUXURY = 'luxury', 'Luxury Hotel'
    RESORT = 'resort', 'Resort'
    BOUTIQUE = 'boutique', 'Boutique Hotel'
    BUSINESS = 'business', 'Business Hotel'


class PartnershipTier(models.TextChoices):
    BRONZE = 'bronze', 'Bronze Partner'
    SILVER = 'silver', 'Silver Partner'
    GOLD = 'gold', 'Gold Partner'
    PLATINUM = 'platinum', 'Platinum Partner'
    EXCLUSIVE = 'exclusive', 'Exclusive Partner'


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Confirmation'
    CONFIRMED = 'confirmed', 'Confirmed'
    CHECKED_IN = 'checked_in', 'Checked In'
    CHECKED_OUT = 'checked_out', 'Checked Out'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'


class RoomType(models.TextChoices):
    STANDARD = 'standard', 'Standard Room'
    DELUXE = 'deluxe', 'Deluxe Room'
    SUITE = 'suite', 'Suite'
    EXECUTIVE = 'executive', 'Executive Room'
    PRESIDENTIAL = 'presidential', 'Presidential Suite'
    FAMILY = 'family', 'Family Room'


class HotelPartner(models.Model):
    """Hotel partners in the platform"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    category = models.CharField(
        max_length=10,
        choices=HotelCategory.choices,
        default=HotelCategory.STANDARD
    )
    
    # Partnership Details
    partnership_tier = models.CharField(
        max_length=10,
        choices=PartnershipTier.choices,
        default=PartnershipTier.BRONZE
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text='Commission rate percentage (0-50%)'
    )
    preferred_partner = models.BooleanField(
        default=False,
        help_text='Shows in premium listings for Premium/VIP users'
    )
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Coordinates
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True
    )
    
    # Contact Information
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Hotel Details
    star_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Hotel star rating (1-5)'
    )
    total_rooms = models.PositiveIntegerField()
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='12:00')
    
    # Amenities (stored as JSON for flexibility)
    amenities = models.JSONField(
        default=list,
        help_text='List of hotel amenities'
    )
    
    # Policies
    cancellation_policy = models.TextField()
    child_policy = models.TextField(blank=True)
    pet_policy = models.TextField(blank=True)
    smoking_policy = models.TextField(blank=True)
    
    # Financial Details
    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=7.50,
        help_text='Tax rate percentage'
    )
    
    # Partnership Status
    is_active = models.BooleanField(default=True)
    partnership_start_date = models.DateField()
    partnership_end_date = models.DateField(null=True, blank=True)
    
    # Performance Metrics
    total_bookings = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    response_time_hours = models.PositiveIntegerField(
        default=24,
        help_text='Average response time for booking confirmations'
    )
    
    # Special Offers for Platform Users
    premium_discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text='Special discount for Premium users (%)'
    )
    vip_discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text='Special discount for VIP users (%)'
    )
    
    # NDPR Compliance
    data_processing_agreement_signed = models.BooleanField(
        default=False,
        help_text='Has signed data processing agreement'
    )
    data_retention_period_days = models.PositiveIntegerField(
        default=365,
        help_text='Days to retain customer data'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hotel_partners'
        indexes = [
            models.Index(fields=['city', 'state']),
            models.Index(fields=['category']),
            models.Index(fields=['partnership_tier']),
            models.Index(fields=['preferred_partner']),
            models.Index(fields=['is_active']),
            models.Index(fields=['average_rating']),
            models.Index(fields=['star_rating']),
        ]
    
    def __str__(self):
        return f'{self.name} - {self.city} ({self.get_partnership_tier_display()})'
    
    def get_discount_for_user_tier(self, user_tier):
        """Get discount rate based on user tier"""
        if user_tier == 'vip':
            return self.vip_discount_rate
        elif user_tier == 'premium':
            return self.premium_discount_rate
        return Decimal('0.00')
    
    def calculate_commission(self, booking_amount):
        """Calculate commission from hotel booking"""
        return booking_amount * (self.commission_rate / 100)
    
    def update_performance_metrics(self):
        """Update hotel performance metrics"""
        bookings = self.hotel_bookings.filter(status__in=['confirmed', 'checked_out'])
        self.total_bookings = bookings.count()
        
        if self.total_bookings > 0:
            ratings = [b.rating for b in bookings if b.rating]
            if ratings:
                self.average_rating = sum(ratings) / len(ratings)
        
        self.save()


class HotelRoom(models.Model):
    """Hotel room types and availability"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    hotel = models.ForeignKey(
        HotelPartner,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    
    # Room Details
    room_type = models.CharField(
        max_length=15,
        choices=RoomType.choices,
        default=RoomType.STANDARD
    )
    room_number = models.CharField(max_length=10, blank=True)
    floor = models.PositiveIntegerField(blank=True, null=True)
    
    # Capacity
    max_adults = models.PositiveIntegerField(default=2)
    max_children = models.PositiveIntegerField(default=0)
    max_occupancy = models.PositiveIntegerField(default=2)
    
    # Room Features
    size_sqm = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Room size in square meters'
    )
    bed_type = models.CharField(
        max_length=50,
        default='Queen Bed',
        help_text='e.g., King Bed, Twin Beds, etc.'
    )
    
    # Amenities specific to room
    room_amenities = models.JSONField(
        default=list,
        help_text='Room-specific amenities'
    )
    
    # Pricing
    base_price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        max_length=3,
        default='NGN'
    )
    
    # Weekend and holiday pricing
    weekend_price_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.20,
        help_text='Weekend price multiplier (1.20 = 20% increase)'
    )
    holiday_price_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.50,
        help_text='Holiday price multiplier'
    )
    
    # Availability
    is_available = models.BooleanField(default=True)
    maintenance_start = models.DateTimeField(null=True, blank=True)
    maintenance_end = models.DateTimeField(null=True, blank=True)
    
    # Images
    images = models.JSONField(
        default=list,
        help_text='List of room image URLs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hotel_rooms'
        indexes = [
            models.Index(fields=['hotel']),
            models.Index(fields=['room_type']),
            models.Index(fields=['is_available']),
            models.Index(fields=['base_price_per_night']),
        ]
    
    def __str__(self):
        return f'{self.hotel.name} - {self.get_room_type_display()}'


class HotelBooking(models.Model):
    """Hotel booking records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Booking Details
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hotel_bookings'
    )
    hotel = models.ForeignKey(
        HotelPartner,
        on_delete=models.CASCADE,
        related_name='hotel_bookings'
    )
    room = models.ForeignKey(
        HotelRoom,
        on_delete=models.CASCADE,
        related_name='room_bookings'
    )
    
    # Dates
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)
    
    # Guest Information
    primary_guest_name = models.CharField(max_length=200)
    primary_guest_phone = models.CharField(max_length=20)
    primary_guest_email = models.EmailField()
    
    number_of_adults = models.PositiveIntegerField(default=1)
    number_of_children = models.PositiveIntegerField(default=0)
    guest_details = models.JSONField(
        default=dict,
        help_text='Additional guest information'
    )
    
    # Booking Status and Timing
    status = models.CharField(
        max_length=15,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    room_rate_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    total_nights = models.PositiveIntegerField()
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    # Discounts and Fees
    user_tier_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Discount based on Premium/VIP status'
    )
    promotional_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    service_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    # Commission
    platform_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    hotel_payout = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Special Requests
    special_requests = models.TextField(blank=True)
    early_check_in_requested = models.BooleanField(default=False)
    late_check_out_requested = models.BooleanField(default=False)
    
    # Integration with Ride Service
    ride_booking = models.ForeignKey(
        'rides.Ride',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hotel_transfer_bookings',
        help_text='Associated ride for hotel transfer'
    )
    airport_pickup_requested = models.BooleanField(default=False)
    hotel_dropoff_requested = models.BooleanField(default=False)
    
    # Cancellation
    cancellation_reason = models.TextField(blank=True)
    cancellation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Review and Rating
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Customer rating (1-5 stars)'
    )
    review = models.TextField(blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    
    # NDPR Compliance
    personal_data_consent = models.BooleanField(
        default=False,
        help_text='Guest consent for data processing'
    )
    marketing_consent = models.BooleanField(
        default=False,
        help_text='Consent for marketing communications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hotel_bookings'
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['hotel']),
            models.Index(fields=['room']),
            models.Index(fields=['status']),
            models.Index(fields=['check_in_date']),
            models.Index(fields=['check_out_date']),
            models.Index(fields=['booked_at']),
            models.Index(fields=['ride_booking']),
        ]
    
    def __str__(self):
        return f'Booking {self.id} - {self.hotel.name} - {self.primary_guest_name}'
