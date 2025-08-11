"""
VIP Ride-Hailing Platform - Simplified Pricing Models
Pricing models without GeoDjango dependencies for easier testing
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import json
from datetime import timedelta
from typing import Tuple, Dict, Any


class PricingZone(models.Model):
    """Geographic pricing zones with simplified boundaries"""
    
    id = models.UUIDField(primary_key=True, default=models.UUIDField().default)
    name = models.CharField(max_length=100, help_text="Zone name")
    description = models.TextField(blank=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='Nigeria')
    
    # Simplified boundary as lat/lng bounds instead of polygon
    min_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    max_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    min_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    max_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    
    # Pricing configuration
    base_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.000'),
        validators=[MinValueValidator(Decimal('0.1')), MaxValueValidator(Decimal('10.0'))],
        help_text="Base pricing multiplier for this zone"
    )
    is_premium_zone = models.BooleanField(default=False)
    
    # Surge configuration
    surge_enabled = models.BooleanField(default=True)
    max_surge_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('5.000'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('10.0'))]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pricing_zones'
        indexes = [
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['is_premium_zone', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.city})"
    
    def contains_point(self, latitude: Decimal, longitude: Decimal) -> bool:
        """Check if a point is within this zone's boundaries"""
        return (
            self.min_latitude <= latitude <= self.max_latitude and
            self.min_longitude <= longitude <= self.max_longitude
        )


class TimeBasedPricing(models.Model):
    """Time-based pricing rules"""
    
    DAY_CHOICES = [
        ('weekday', 'Weekday (Monday-Friday)'),
        ('weekend', 'Weekend (Saturday-Sunday)'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('all', 'All Days'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Time configuration
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Date range (optional)
    date_from = models.DateField(null=True, blank=True)
    date_until = models.DateField(null=True, blank=True)
    
    # Pricing multipliers
    multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.000'),
        validators=[MinValueValidator(Decimal('0.1')), MaxValueValidator(Decimal('10.0'))]
    )
    
    # Tier-specific multipliers
    normal_tier_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.000')
    )
    premium_tier_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.100')
    )
    vip_tier_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.200')
    )
    
    # Priority and status
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'time_based_pricing'
        ordering = ['-priority', 'start_time']
    
    def __str__(self):
        return f"{self.name} ({self.day_of_week} {self.start_time}-{self.end_time})"
    
    def is_applicable_now(self) -> bool:
        """Check if this rule applies to current time"""
        now = timezone.now()
        current_time = now.time()
        current_date = now.date()
        current_weekday = now.strftime('%A').lower()
        
        # Check date range
        if self.date_from and current_date < self.date_from:
            return False
        if self.date_until and current_date > self.date_until:
            return False
        
        # Check day of week
        if self.day_of_week == 'weekday' and current_weekday in ['saturday', 'sunday']:
            return False
        elif self.day_of_week == 'weekend' and current_weekday not in ['saturday', 'sunday']:
            return False
        elif self.day_of_week not in ['weekday', 'weekend', 'all'] and self.day_of_week != current_weekday:
            return False
        
        # Check time range
        if self.start_time <= self.end_time:
            return self.start_time <= current_time <= self.end_time
        else:
            # Handle overnight time ranges
            return current_time >= self.start_time or current_time <= self.end_time


class SpecialEvent(models.Model):
    """Special events affecting pricing"""
    
    class EventType(models.TextChoices):
        CONCERT = 'concert', 'Concert'
        SPORTS = 'sports', 'Sports Event'
        CONFERENCE = 'conference', 'Conference'
        FESTIVAL = 'festival', 'Festival'
        HOLIDAY = 'holiday', 'Holiday'
        WEATHER = 'weather', 'Weather Event'
        EMERGENCY = 'emergency', 'Emergency'
        OTHER = 'other', 'Other'
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    venue_name = models.CharField(max_length=200, blank=True)
    organizer = models.CharField(max_length=200, blank=True)
    
    # Event timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    # Location (simplified as lat/lng)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    affected_zones = models.ManyToManyField(PricingZone, blank=True)
    
    # Pricing configuration
    base_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.500'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('10.0'))]
    )
    peak_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('2.000'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('10.0'))]
    )
    
    # Peak timing offsets
    peak_start_offset = models.DurationField(
        default=timedelta(minutes=-30),
        help_text="Peak starts this duration before event start"
    )
    peak_end_offset = models.DurationField(
        default=timedelta(minutes=60),
        help_text="Peak ends this duration after event start"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'special_events'
        indexes = [
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['event_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_datetime.date()})"
    
    def is_active_now(self) -> bool:
        """Check if event is currently active"""
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime
    
    def get_current_multiplier(self) -> Decimal:
        """Get current multiplier based on time within event"""
        now = timezone.now()
        
        if not self.is_active_now():
            return Decimal('1.000')
        
        # Calculate peak period
        peak_start = self.start_datetime + self.peak_start_offset
        peak_end = self.start_datetime + self.peak_end_offset
        
        if peak_start <= now <= peak_end:
            return self.peak_multiplier
        else:
            return self.base_multiplier


class DemandSurge(models.Model):
    """Real-time demand surge data"""
    
    SURGE_LEVELS = [
        ('none', 'No Surge'),
        ('low', 'Low Surge'),
        ('medium', 'Medium Surge'),
        ('high', 'High Surge'),
        ('very_high', 'Very High Surge'),
        ('extreme', 'Extreme Surge'),
    ]
    
    zone = models.ForeignKey(PricingZone, on_delete=models.CASCADE)
    
    # Demand metrics
    active_rides = models.IntegerField(default=0)
    pending_requests = models.IntegerField(default=0)
    available_drivers = models.IntegerField(default=0)
    demand_ratio = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal('1.000')
    )
    
    # Surge calculation
    surge_level = models.CharField(max_length=10, choices=SURGE_LEVELS, default='none')
    surge_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.000'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('10.0'))]
    )
    
    # Validity
    calculated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'demand_surge'
        indexes = [
            models.Index(fields=['zone', 'is_active', 'expires_at']),
            models.Index(fields=['calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.zone.name} - {self.surge_level} ({self.surge_multiplier}x)"
    
    def is_valid(self) -> bool:
        """Check if surge data is still valid"""
        return self.is_active and timezone.now() < self.expires_at
    
    def calculate_surge_level(self) -> Tuple[str, Decimal]:
        """Calculate surge level and multiplier based on demand ratio"""
        ratio = self.demand_ratio
        
        if ratio <= Decimal('1.2'):
            return 'none', Decimal('1.000')
        elif ratio <= Decimal('2.0'):
            return 'low', Decimal('1.200')
        elif ratio <= Decimal('3.0'):
            return 'medium', Decimal('1.500')
        elif ratio <= Decimal('5.0'):
            return 'high', Decimal('2.000')
        elif ratio <= Decimal('8.0'):
            return 'very_high', Decimal('3.000')
        else:
            return 'extreme', min(Decimal('5.000'), self.zone.max_surge_multiplier)


class PromotionalCode(models.Model):
    """Promotional codes and discounts"""
    
    class CodeType(models.TextChoices):
        DISCOUNT = 'discount', 'Regular Discount'
        FIRST_RIDE = 'first_ride', 'First Ride Discount'
        SURGE_WAIVER = 'surge_waiver', 'Surge Waiver'
        TIER_UPGRADE = 'tier_upgrade', 'Tier Upgrade'
        CASHBACK = 'cashback', 'Cashback'
    
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED_AMOUNT = 'fixed_amount', 'Fixed Amount'
        FREE_RIDE = 'free_ride', 'Free Ride'
    
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    
    # Code configuration
    code_type = models.CharField(max_length=20, choices=CodeType.choices)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Percentage (0-100) or fixed amount"
    )
    
    # Constraints
    minimum_trip_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    maximum_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    
    # Usage limits
    max_uses = models.IntegerField(default=0, help_text="0 = unlimited")
    max_uses_per_user = models.IntegerField(default=1)
    usage_count = models.IntegerField(default=0)
    first_ride_only = models.BooleanField(default=False)
    
    # Eligibility
    eligible_tiers = models.JSONField(default=list, blank=True)
    applies_to_surge = models.BooleanField(default=False)
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promotional_codes'
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['expires_at', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.description}"
    
    def can_user_use(self, user) -> Tuple[bool, str]:
        """Check if user can use this promotional code"""
        # Check if code is active and not expired
        if not self.is_active:
            return False, "This promo code is no longer active"
        
        if timezone.now() > self.expires_at:
            return False, "This promo code has expired"
        
        if timezone.now() < self.valid_from:
            return False, "This promo code is not yet valid"
        
        # Check global usage limit
        if self.max_uses > 0 and self.usage_count >= self.max_uses:
            return False, "This promo code has reached its usage limit"
        
        # Check tier eligibility
        if self.eligible_tiers and user.tier not in self.eligible_tiers:
            return False, "This promo code is not available for your membership tier"
        
        # Check user-specific usage (simplified - would need proper tracking)
        if self.first_ride_only:
            # This would need proper ride history check
            pass
        
        return True, "Valid"
    
    def calculate_discount(self, amount: Decimal, user_tier: str) -> Decimal:
        """Calculate discount amount for given trip amount"""
        if amount < self.minimum_trip_amount:
            return Decimal('0.00')
        
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = amount * (self.discount_value / 100)
        elif self.discount_type == self.DiscountType.FIXED_AMOUNT:
            discount = self.discount_value
        elif self.discount_type == self.DiscountType.FREE_RIDE:
            discount = amount
        else:
            discount = Decimal('0.00')
        
        # Apply maximum discount limit
        if self.maximum_discount:
            discount = min(discount, self.maximum_discount)
        
        return discount


class PricingRule(models.Model):
    """Base pricing rules for different vehicle types and zones"""
    
    VEHICLE_TYPES = [
        ('economy', 'Economy'),
        ('comfort', 'Comfort'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury'),
        ('suv', 'SUV'),
        ('van', 'Van'),
    ]
    
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    zone = models.ForeignKey(PricingZone, on_delete=models.CASCADE)
    
    # Base pricing
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_minute_rate = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_fare = models.DecimalField(max_digits=10, decimal_places=2)
    booking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Tier multipliers
    normal_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.000')
    )
    premium_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.100')
    )
    vip_multiplier = models.DecimalField(
        max_digits=5, decimal_places=3, default=Decimal('1.200')
    )
    
    # Validity
    effective_from = models.DateTimeField(default=timezone.now)
    effective_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pricing_rules'
        unique_together = ['vehicle_type', 'zone', 'effective_from']
        indexes = [
            models.Index(fields=['vehicle_type', 'zone', 'is_active']),
            models.Index(fields=['effective_from', 'effective_until']),
        ]
    
    def __str__(self):
        return f"{self.vehicle_type} - {self.zone.name}"


class PriceCalculationLog(models.Model):
    """Audit log for price calculations (transparency)"""
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    # Trip details
    pickup_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    pickup_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    dropoff_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    dropoff_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_duration_minutes = models.IntegerField()
    vehicle_type = models.CharField(max_length=20)
    
    # Base calculation
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    distance_fare = models.DecimalField(max_digits=10, decimal_places=2)
    time_fare = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Multipliers applied
    zone_multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('1.000'))
    time_multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('1.000'))
    surge_multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('1.000'))
    event_multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('1.000'))
    tier_multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('1.000'))
    
    # Final pricing
    total_before_discount = models.DecimalField(max_digits=10, decimal_places=2)
    promo_discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    applied_promo_code = models.CharField(max_length=20, blank=True)
    
    # Metadata
    pricing_factors = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'price_calculation_logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Price calculation for {self.user.email} - ₦{self.final_price}"
