# payments/models.py
"""
VIP Ride-Hailing Platform - Payment Processing Models
Multi-gateway, multi-currency payment system with PCI DSS compliance
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
import json
from cryptography.fernet import Fernet
from accounts.models import UserTier


class Currency(models.Model):
    """Supported currencies with real-time exchange rates"""
    code = models.CharField(max_length=3, unique=True, help_text="ISO 4217 currency code")
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    decimal_places = models.PositiveIntegerField(default=2)
    
    # Exchange rate management
    usd_exchange_rate = models.DecimalField(
        max_digits=12, 
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))],
        help_text="Current rate to convert to USD"
    )
    last_rate_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Regional settings
    is_default = models.BooleanField(default=False)
    supported_regions = models.JSONField(default=list)
    
    class Meta:
        db_table = 'payment_currencies'
        verbose_name_plural = 'Currencies'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def convert_to_usd(self, amount):
        """Convert amount from this currency to USD"""
        return Decimal(str(amount)) / self.usd_exchange_rate
    
    def convert_from_usd(self, usd_amount):
        """Convert USD amount to this currency"""
        return Decimal(str(usd_amount)) * self.usd_exchange_rate


class PaymentGateway(models.Model):
    """Payment gateway configurations"""
    
    class GatewayType(models.TextChoices):
        PAYSTACK = 'paystack', 'Paystack'
        FLUTTERWAVE = 'flutterwave', 'Flutterwave'
        STRIPE = 'stripe', 'Stripe'
        RAZORPAY = 'razorpay', 'Razorpay'
        PAYPAL = 'paypal', 'PayPal'
    
    name = models.CharField(max_length=50)
    gateway_type = models.CharField(max_length=20, choices=GatewayType.choices)
    
    # Configuration (encrypted)
    encrypted_config = models.TextField(help_text="Encrypted API keys and config")
    
    # Supported features
    supported_currencies = models.ManyToManyField(Currency, related_name='gateways')
    supports_payouts = models.BooleanField(default=False)
    supports_disputes = models.BooleanField(default=False)
    supports_subscriptions = models.BooleanField(default=False)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    priority_order = models.PositiveIntegerField(default=1)
    
    # Transaction fees
    percentage_fee = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0290'))
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Regional availability
    supported_countries = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_gateways'
        indexes = [
            models.Index(fields=['gateway_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['priority_order']),
        ]
        ordering = ['priority_order']
    
    def __str__(self):
        return f"{self.name} ({self.gateway_type})"
    
    def encrypt_config(self, config_data):
        """Encrypt gateway configuration (PCI DSS compliance)"""
        try:
            from django.conf import settings
            import base64
            key = base64.urlsafe_b64encode(
                settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            )
            fernet = Fernet(key)
            return fernet.encrypt(json.dumps(config_data).encode()).decode()
        except Exception as e:
            # Log the error and raise exception to prevent storing unencrypted data
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to encrypt gateway config: {e}")
            raise ValueError("Failed to encrypt sensitive configuration data")
    
    def decrypt_config(self):
        """Decrypt gateway configuration"""
        if not self.encrypted_config:
            return {}
        
        try:
            from django.conf import settings
            import base64
            key = base64.urlsafe_b64encode(
                settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            )
            fernet = Fernet(key)
            decrypted = fernet.decrypt(self.encrypted_config.encode()).decode()
            return json.loads(decrypted)
        except Exception:
            try:
                return json.loads(self.encrypted_config)
            except Exception:
                return {}
    
    def calculate_total_fee(self, amount):
        """Calculate total fee for transaction amount"""
        percentage_fee = (Decimal(str(amount)) * self.percentage_fee)
        return percentage_fee + self.fixed_fee


class PaymentMethod(models.Model):
    """Customer payment methods (tokenized for PCI compliance)"""
    
    class MethodType(models.TextChoices):
        CARD = 'card', 'Credit/Debit Card'
        BANK_ACCOUNT = 'bank_account', 'Bank Account'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        WALLET = 'wallet', 'Digital Wallet'
        CRYPTO = 'crypto', 'Cryptocurrency'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    
    method_type = models.CharField(max_length=20, choices=MethodType.choices)
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    
    # Tokenized data (PCI DSS compliant)
    gateway_token = models.CharField(max_length=200, help_text="Gateway's token for payment method")
    
    # Safe display information
    last_four_digits = models.CharField(max_length=4, blank=True)
    brand = models.CharField(max_length=50, blank=True, help_text="Card brand or bank name")
    expiry_month = models.PositiveIntegerField(null=True, blank=True)
    expiry_year = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['gateway']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.method_type} ending in {self.last_four_digits}"


class Payment(models.Model):
    """Payment transactions with multi-gateway support"""
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'
        PARTIALLY_REFUNDED = 'partially_refunded', 'Partially Refunded'
        DISPUTED = 'disputed', 'Disputed'
        CHARGEBACK = 'chargeback', 'Chargeback'
    
    class PaymentType(models.TextChoices):
        RIDE_PAYMENT = 'ride_payment', 'Ride Payment'
        CANCELLATION_FEE = 'cancellation_fee', 'Cancellation Fee'
        SUBSCRIPTION = 'subscription', 'Subscription'
        DRIVER_PAYOUT = 'driver_payout', 'Driver Payout'
        REFUND = 'refund', 'Refund'
        COMMISSION = 'commission', 'Commission'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core payment info
    ride = models.ForeignKey(
        'rides.Ride', 
        on_delete=models.CASCADE, 
        related_name='payments',
        null=True, 
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    # Amount and currency
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    usd_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount in USD for reporting")
    
    # Gateway and method
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Gateway transaction details
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_reference = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Fee breakdown
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount after fees")
    
    # Commission calculation (tier-based)
    user_tier = models.CharField(max_length=10, choices=UserTier.choices)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.0'))
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    driver_payout_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Timing
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    failure_reason = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Metadata and compliance
    customer_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # PCI DSS compliance fields
    is_test_transaction = models.BooleanField(default=False)
    pci_compliance_level = models.CharField(max_length=20, default='LEVEL_1')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        indexes = [
            models.Index(fields=['ride']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_type']),
            models.Index(fields=['gateway']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user_tier']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency.code} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate net_amount automatically"""
        gateway_fee = self.gateway_fee or Decimal('0.00')
        platform_fee = self.platform_fee or Decimal('0.00')
        self.net_amount = self.amount - gateway_fee - platform_fee
        super().save(*args, **kwargs)
    
    def calculate_commission(self):
        """Calculate commission based on user tier"""
        commission_rates = {
            UserTier.NORMAL: Decimal('0.15'),  # 15%
            UserTier.PREMIUM: Decimal('0.225'),  # 22.5%
            UserTier.VIP: Decimal('0.275'),  # 27.5%
        }
        
        rate = commission_rates.get(self.user_tier, commission_rates[UserTier.NORMAL])
        self.commission_rate = rate * 100  # Store as percentage
        
        # Ensure gateway_fee is not None and use Decimal arithmetic with rounding
        gateway_fee = self.gateway_fee or Decimal('0.00')
        self.commission_amount = (self.amount * rate).quantize(Decimal("0.01"))
        self.driver_payout_amount = (self.amount - self.commission_amount - gateway_fee).quantize(Decimal("0.01"))
        
        return self.commission_amount
    
    def convert_to_currency(self, target_currency_code):
        """Convert payment amount to target currency"""
        if self.currency.code == target_currency_code:
            return self.amount
        
        target_currency = Currency.objects.get(code=target_currency_code, is_active=True)
        usd_amount = self.currency.convert_to_usd(self.amount)
        return target_currency.convert_from_usd(usd_amount)


class PaymentDispute(models.Model):
    """Payment dispute management"""
    
    class DisputeStatus(models.TextChoices):
        CREATED = 'created', 'Created'
        INVESTIGATING = 'investigating', 'Under Investigation'
        EVIDENCE_REQUIRED = 'evidence_required', 'Evidence Required'
        EVIDENCE_SUBMITTED = 'evidence_submitted', 'Evidence Submitted'
        RESOLVED_WON = 'resolved_won', 'Resolved - Won'
        RESOLVED_LOST = 'resolved_lost', 'Resolved - Lost'
        EXPIRED = 'expired', 'Expired'
    
    class DisputeReason(models.TextChoices):
        FRAUDULENT = 'fraudulent', 'Fraudulent Transaction'
        DUPLICATE = 'duplicate', 'Duplicate Charge'
        UNRECOGNIZED = 'unrecognized', 'Unrecognized Charge'
        SERVICE_NOT_RECEIVED = 'service_not_received', 'Service Not Received'
        POOR_SERVICE = 'poor_service', 'Poor Service Quality'
        CANCELLATION = 'cancellation', 'Cancellation Issue'
        OTHER = 'other', 'Other'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    payment = models.OneToOneField(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='dispute'
    )
    
    # Dispute details
    dispute_reason = models.CharField(max_length=30, choices=DisputeReason.choices)
    status = models.CharField(max_length=20, choices=DisputeStatus.choices, default=DisputeStatus.CREATED)
    
    # Amounts
    disputed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    
    # Gateway dispute ID
    gateway_dispute_id = models.CharField(max_length=200, blank=True)
    
    # Timeline
    dispute_date = models.DateTimeField()
    evidence_due_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    # Evidence and documentation
    customer_message = models.TextField(blank=True)
    merchant_response = models.TextField(blank=True)
    evidence_files = models.JSONField(default=list, blank=True)
    
    # Resolution
    resolution_outcome = models.CharField(max_length=20, blank=True)
    resolution_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Internal tracking
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_disputes'
    )
    internal_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_disputes'
        indexes = [
            models.Index(fields=['payment']),
            models.Index(fields=['status']),
            models.Index(fields=['dispute_reason']),
            models.Index(fields=['evidence_due_date']),
            models.Index(fields=['assigned_to']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dispute {self.id} - {self.disputed_amount} {self.currency.code} - {self.status}"


class DriverPayout(models.Model):
    """Driver payout management system"""
    
    class PayoutStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
        ON_HOLD = 'on_hold', 'On Hold'
    
    class PayoutMethod(models.TextChoices):
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        WALLET = 'wallet', 'Digital Wallet'
        CHECK = 'check', 'Check'
        CASH = 'cash', 'Cash'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    driver = models.ForeignKey(
        'accounts.Driver',
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    
    # Payout details
    status = models.CharField(max_length=15, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    payout_method = models.CharField(max_length=20, choices=PayoutMethod.choices)
    
    # Amount calculation
    gross_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    commission_deducted = models.DecimalField(max_digits=10, decimal_places=2)
    gateway_fees_deducted = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_deducted = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_payout_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    
    # Period covered
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Payment processing
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT, null=True, blank=True)
    gateway_payout_id = models.CharField(max_length=200, blank=True)
    
    # Bank details (encrypted)
    encrypted_bank_details = models.TextField(blank=True)
    
    # Timing
    scheduled_date = models.DateTimeField()
    processed_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Associated rides and payments
    rides = models.ManyToManyField('rides.Ride', related_name='driver_payouts', blank=True)
    payments = models.ManyToManyField(Payment, related_name='driver_payouts', blank=True)
    
    # Failure handling
    failure_reason = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Compliance and audit
    tax_document_generated = models.BooleanField(default=False)
    compliance_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'driver_payouts'
        indexes = [
            models.Index(fields=['driver']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout {self.id} - {self.driver.user.get_full_name()} - {self.net_payout_amount} {self.currency.code}"
    
    def encrypt_bank_details(self, bank_data):
        """Encrypt bank details for PCI DSS compliance"""
        try:
            from django.conf import settings
            import base64
            key = base64.urlsafe_b64encode(
                settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            )
            fernet = Fernet(key)
            return fernet.encrypt(json.dumps(bank_data).encode()).decode()
        except Exception as e:
            # Log the error and raise exception to prevent storing unencrypted bank details
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to encrypt bank details: {e}")
            raise ValueError("Failed to encrypt sensitive bank information")
    
    def decrypt_bank_details(self):
        """Decrypt bank details"""
        if not self.encrypted_bank_details:
            return {}
        
        try:
            from django.conf import settings
            import base64
            key = base64.urlsafe_b64encode(
                settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            )
            fernet = Fernet(key)
            decrypted = fernet.decrypt(self.encrypted_bank_details.encode()).decode()
            return json.loads(decrypted)
        except Exception:
            try:
                return json.loads(self.encrypted_bank_details)
            except Exception:
                return {}


class ExchangeRate(models.Model):
    """Historical exchange rates for currency conversion"""
    
    base_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='base_rates')
    target_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='target_rates')
    
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    rate_source = models.CharField(max_length=50, default='API')  # API provider
    
    # Timing
    effective_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exchange_rates'
        unique_together = ['base_currency', 'target_currency', 'effective_date']
        indexes = [
            models.Index(fields=['base_currency', 'target_currency']),
            models.Index(fields=['effective_date']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.base_currency.code}/{self.target_currency.code} = {self.rate} ({self.effective_date})"


class PaymentAuditLog(models.Model):
    """Audit log for payment-related activities (PCI DSS compliance)"""
    
    class ActionType(models.TextChoices):
        PAYMENT_CREATED = 'payment_created', 'Payment Created'
        PAYMENT_PROCESSED = 'payment_processed', 'Payment Processed'
        PAYMENT_FAILED = 'payment_failed', 'Payment Failed'
        REFUND_ISSUED = 'refund_issued', 'Refund Issued'
        DISPUTE_CREATED = 'dispute_created', 'Dispute Created'
        PAYOUT_PROCESSED = 'payout_processed', 'Payout Processed'
        CONFIG_CHANGED = 'config_changed', 'Configuration Changed'
        ACCESS_GRANTED = 'access_granted', 'Access Granted'
        ACCESS_DENIED = 'access_denied', 'Access Denied'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What happened
    action_type = models.CharField(max_length=30, choices=ActionType.choices)
    description = models.TextField()
    
    # Who did it
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # What was affected
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    dispute = models.ForeignKey(PaymentDispute, on_delete=models.SET_NULL, null=True, blank=True)
    payout = models.ForeignKey(DriverPayout, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional context
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_audit_logs'
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['user']),
            models.Index(fields=['payment']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action_type} - {self.timestamp} - {self.user}"
