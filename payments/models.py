from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid


class Currency(models.TextChoices):
    NGN = 'NGN', 'Nigerian Naira'
    USD = 'USD', 'US Dollar'
    EUR = 'EUR', 'Euro'
    GBP = 'GBP', 'British Pound'
    ZAR = 'ZAR', 'South African Rand'
    GHS = 'GHS', 'Ghanaian Cedi'
    KES = 'KES', 'Kenyan Shilling'


class PaymentMethod(models.TextChoices):
    CARD = 'card', 'Credit/Debit Card'
    MOBILE_MONEY = 'mobile_money', 'Mobile Money'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    WALLET = 'wallet', 'Digital Wallet'
    CASH = 'cash', 'Cash Payment'
    CORPORATE_ACCOUNT = 'corporate_account', 'Corporate Account'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'
    PARTIALLY_REFUNDED = 'partially_refunded', 'Partially Refunded'


class PaymentType(models.TextChoices):
    RIDE_PAYMENT = 'ride_payment', 'Ride Payment'
    HOTEL_BOOKING = 'hotel_booking', 'Hotel Booking Payment'
    DRIVER_SUBSCRIPTION = 'driver_subscription', 'Driver Subscription'
    COMMISSION_PAYOUT = 'commission_payout', 'Commission Payout'
    REFUND = 'refund', 'Refund Payment'
    CANCELLATION_FEE = 'cancellation_fee', 'Cancellation Fee'
    LEASE_PAYMENT = 'lease_payment', 'Vehicle Lease Payment'
    PENALTY = 'penalty', 'Penalty Payment'


class SubscriptionTier(models.TextChoices):
    BASIC = 'basic', 'Basic Driver ($99/month)'
    STANDARD = 'standard', 'Standard Driver ($149/month)'
    PREMIUM = 'premium', 'Premium Driver ($199/month)'
    VIP = 'vip', 'VIP Driver ($299/month)'


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    CANCELLED = 'cancelled', 'Cancelled'
    SUSPENDED = 'suspended', 'Suspended'
    EXPIRED = 'expired', 'Expired'
    PENDING = 'pending', 'Pending Activation'


class ExchangeRate(models.Model):
    """Exchange rates for multi-currency support"""
    base_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.NGN
    )
    target_currency = models.CharField(
        max_length=3,
        choices=Currency.choices
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text='Rate to convert 1 unit of base currency to target currency'
    )
    
    # Rate metadata
    source = models.CharField(
        max_length=50,
        default='manual',
        help_text='Source of exchange rate (manual, api, bank)'
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exchange_rates'
        unique_together = ('base_currency', 'target_currency')
        indexes = [
            models.Index(fields=['base_currency', 'target_currency']),
            models.Index(fields=['is_active', 'updated_at']),
        ]
    
    def __str__(self):
        return f'{self.base_currency}/{self.target_currency}: {self.rate}'


class Payment(models.Model):
    """Enhanced payment model with multi-currency and subscription support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core payment info
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.RIDE_PAYMENT
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Parties involved
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_made'
    )
    payee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_received'
    )
    
    # Related objects
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ride_payments'
    )
    hotel_booking = models.ForeignKey(
        'hotels.HotelBooking',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='booking_payments'
    )
    vehicle_lease = models.ForeignKey(
        'vehicle_leasing.VehicleLease',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lease_payments'
    )
    
    # Multi-currency amounts
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Amount in original currency'
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.NGN
    )
    
    # Converted amounts (for accounting in base currency)
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Amount converted to base currency (NGN)'
    )
    exchange_rate_used = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Exchange rate used for conversion'
    )
    
    # Payment method details
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD
    )
    
    # Gateway information
    payment_gateway = models.CharField(
        max_length=50,
        blank=True,
        help_text='Payment processor used (e.g., Paystack, Flutterwave)'
    )
    gateway_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Transaction ID from payment gateway'
    )
    gateway_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Gateway reference number'
    )
    
    # Fee breakdown
    gateway_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    platform_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Amount after all fees'
    )
    
    # Commission breakdown for ride payments
    driver_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    fleet_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    platform_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    vehicle_owner_share = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Timing
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Failure information
    failure_reason = models.TextField(blank=True)
    failure_code = models.CharField(max_length=50, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Refund information
    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional payment metadata'
    )
    
    # NDPR compliance
    personal_data_processed = models.BooleanField(
        default=False,
        help_text='Whether personal data was processed for this payment'
    )
    data_processing_purpose = models.CharField(
        max_length=200,
        blank=True,
        help_text='Purpose of personal data processing'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        indexes = [
            models.Index(fields=['payer']),
            models.Index(fields=['payee']),
            models.Index(fields=['ride']),
            models.Index(fields=['hotel_booking']),
            models.Index(fields=['vehicle_lease']),
            models.Index(fields=['payment_type']),
            models.Index(fields=['status']),
            models.Index(fields=['currency']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['initiated_at']),
            models.Index(fields=['completed_at']),
        ]
    
    def __str__(self):
        return f'Payment {self.id} - {self.amount} {self.currency} - {self.get_status_display()}'
    
    def convert_currency(self, target_currency):
        """Convert payment amount to target currency"""
        if self.currency == target_currency:
            return self.amount
        
        try:
            exchange_rate = ExchangeRate.objects.get(
                base_currency=self.currency,
                target_currency=target_currency,
                is_active=True
            )
            return self.amount * exchange_rate.rate
        except ExchangeRate.DoesNotExist:
            # Try reverse conversion
            try:
                exchange_rate = ExchangeRate.objects.get(
                    base_currency=target_currency,
                    target_currency=self.currency,
                    is_active=True
                )
                return self.amount / exchange_rate.rate
            except ExchangeRate.DoesNotExist:
                return self.amount  # Return original if no rate found
    
    def calculate_commission_breakdown(self):
        """Calculate commission breakdown based on payment type and relationships"""
        if self.payment_type != PaymentType.RIDE_PAYMENT or not self.ride:
            return
        
        ride = self.ride
        
        # Platform commission based on customer tier
        if ride.customer_tier == 'normal':
            platform_rate = Decimal('0.175')  # 17.5% average
        elif ride.customer_tier == 'premium':
            platform_rate = Decimal('0.225')  # 22.5% average
        else:  # VIP
            platform_rate = Decimal('0.275')  # 27.5% average
        
        self.platform_commission = self.net_amount * platform_rate
        
        # Remaining amount for distribution
        remaining = self.net_amount - self.platform_commission
        
        if ride.fleet_company:
            # Fleet ride - share between driver and fleet
            fleet_share_rate = Decimal('0.20')  # 20% to fleet
            self.fleet_commission = remaining * fleet_share_rate
            self.driver_commission = remaining - self.fleet_commission
            
            # If vehicle is leased, allocate owner share
            if ride.vehicle and hasattr(ride.vehicle, 'current_lease'):
                lease = ride.vehicle.current_lease
                if lease and lease.status == 'active':
                    owner_share_rate = Decimal('0.15')  # 15% to vehicle owner
                    self.vehicle_owner_share = remaining * owner_share_rate
                    self.fleet_commission -= self.vehicle_owner_share
        else:
            # Private driver gets full remaining amount
            self.driver_commission = remaining
    
    def mark_completed(self):
        """Mark payment as completed and update timestamps"""
        self.status = PaymentStatus.COMPLETED
        self.completed_at = timezone.now()
        if not self.processed_at:
            self.processed_at = timezone.now()
        self.calculate_commission_breakdown()
        self.save()
    
    def mark_failed(self, reason='', code=''):
        """Mark payment as failed with reason"""
        self.status = PaymentStatus.FAILED
        self.failed_at = timezone.now()
        self.failure_reason = reason
        self.failure_code = code
        self.save()
    
    def can_retry(self):
        """Check if payment can be retried"""
        return (
            self.status == PaymentStatus.FAILED and
            self.retry_count < self.max_retries
        )


class DriverSubscription(models.Model):
    """Driver subscription model for tiered access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    driver = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_subscription'
    )
    
    # Subscription details
    tier = models.CharField(
        max_length=10,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.BASIC
    )
    status = models.CharField(
        max_length=10,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.PENDING
    )
    
    # Pricing (multi-currency)
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.NGN
    )
    
    # Subscription period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    next_billing_date = models.DateTimeField()
    
    # Payment information
    last_payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscription_payments'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD
    )
    
    # Subscription benefits tracking
    monthly_ride_limit = models.PositiveIntegerField(
        default=100,
        help_text='Maximum rides per month for this tier'
    )
    current_month_rides = models.PositiveIntegerField(default=0)
    priority_level = models.PositiveIntegerField(
        default=1,
        help_text='1=Lowest, 5=Highest priority for ride allocation'
    )
    
    # Features enabled
    can_accept_premium_rides = models.BooleanField(default=False)
    can_accept_vip_rides = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    can_set_custom_rates = models.BooleanField(default=False)
    
    # Billing history
    total_payments_made = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    consecutive_payment_months = models.PositiveIntegerField(default=0)
    missed_payments = models.PositiveIntegerField(default=0)
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Auto-renewal
    auto_renewal_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'driver_subscriptions'
        indexes = [
            models.Index(fields=['driver']),
            models.Index(fields=['tier']),
            models.Index(fields=['status']),
            models.Index(fields=['next_billing_date']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f'{self.driver.get_full_name()} - {self.get_tier_display()} - {self.get_status_display()}'
    
    @property
    def is_active(self):
        return (
            self.status == SubscriptionStatus.ACTIVE and
            self.end_date > timezone.now()
        )
    
    @property
    def is_expired(self):
        return self.end_date <= timezone.now()
    
    @property
    def days_until_expiry(self):
        if self.is_expired:
            return 0
        return (self.end_date - timezone.now()).days
    
    def get_tier_benefits(self):
        """Get benefits for current subscription tier"""
        benefits = {
            SubscriptionTier.BASIC: {
                'monthly_fee_usd': 99,
                'ride_limit': 100,
                'priority_level': 1,
                'premium_rides': False,
                'vip_rides': False,
                'priority_support': False,
                'custom_rates': False,
            },
            SubscriptionTier.STANDARD: {
                'monthly_fee_usd': 149,
                'ride_limit': 200,
                'priority_level': 2,
                'premium_rides': True,
                'vip_rides': False,
                'priority_support': False,
                'custom_rates': False,
            },
            SubscriptionTier.PREMIUM: {
                'monthly_fee_usd': 199,
                'ride_limit': 400,
                'priority_level': 3,
                'premium_rides': True,
                'vip_rides': True,
                'priority_support': True,
                'custom_rates': True,
            },
            SubscriptionTier.VIP: {
                'monthly_fee_usd': 299,
                'ride_limit': 1000,
                'priority_level': 5,
                'premium_rides': True,
                'vip_rides': True,
                'priority_support': True,
                'custom_rates': True,
            },
        }
        return benefits.get(self.tier, benefits[SubscriptionTier.BASIC])
    
    def apply_tier_benefits(self):
        """Apply benefits based on current tier"""
        benefits = self.get_tier_benefits()
        
        self.monthly_ride_limit = benefits['ride_limit']
        self.priority_level = benefits['priority_level']
        self.can_accept_premium_rides = benefits['premium_rides']
        self.can_accept_vip_rides = benefits['vip_rides']
        self.has_priority_support = benefits['priority_support']
        self.can_set_custom_rates = benefits['custom_rates']
        
        self.save()
    
    def can_accept_ride(self, ride_type):
        """Check if driver can accept a specific ride type based on subscription"""
        if not self.is_active:
            return False
        
        if self.current_month_rides >= self.monthly_ride_limit:
            return False
        
        if ride_type == 'premium' and not self.can_accept_premium_rides:
            return False
        
        if ride_type == 'vip' and not self.can_accept_vip_rides:
            return False
        
        return True
    
    def process_monthly_billing(self):
        """Process monthly subscription billing"""
        from .tasks import process_subscription_payment
        
        if self.auto_renewal_enabled and self.is_active:
            # Create payment for next month
            process_subscription_payment.delay(self.id)
    
    def upgrade_tier(self, new_tier):
        """Upgrade subscription to higher tier"""
        tier_hierarchy = [
            SubscriptionTier.BASIC,
            SubscriptionTier.STANDARD,
            SubscriptionTier.PREMIUM,
            SubscriptionTier.VIP
        ]
        
        current_index = tier_hierarchy.index(self.tier)
        new_index = tier_hierarchy.index(new_tier)
        
        if new_index > current_index:
            self.tier = new_tier
            self.apply_tier_benefits()
            
            # Calculate prorated amount for immediate payment
            benefits = self.get_tier_benefits()
            # Implementation for prorated billing would go here
            
            return True
        return False
    
    def cancel_subscription(self, reason=''):
        """Cancel subscription"""
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.auto_renewal_enabled = False
        self.save()
