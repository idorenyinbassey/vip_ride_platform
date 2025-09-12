from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Generate username from email if not provided
        if not extra_fields.get('username'):
            username_base = email.split('@')[0]
            username = username_base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            extra_fields['username'] = username
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)


class UserTier(models.TextChoices):
    NORMAL = 'normal', 'Normal'
    VIP = 'vip', 'VIP'
    VIP_PREMIUM = 'vip_premium', 'VIP Premium'


class UserType(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Customer'
    DRIVER = 'DRIVER', 'Driver'
    FLEET_OWNER = 'FLEET_OWNER', 'Fleet Owner'
    VEHICLE_OWNER = 'VEHICLE_OWNER', 'Vehicle Owner'
    ADMIN = 'ADMIN', 'Admin'


class DriverCategory(models.TextChoices):
    PRIVATE = 'private', 'Private Driver'
    FLEET_EMPLOYEE = 'fleet_employee', 'Fleet Employee'
    OWNER_OPERATOR = 'owner_operator', 'Owner Operator'


class User(AbstractUser):
    # Override username to make it optional
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text='Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[UnicodeUsernameValidator()],
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    tier = models.CharField(
        max_length=15,
        choices=UserTier.choices,
        default=UserTier.NORMAL
    )
    
    # Profile Information
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Nigeria')
    
    # Verification
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_identity_verified = models.BooleanField(default=False)
    
    # Account Status
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    
    # MFA (Multi-Factor Authentication) Settings
    mfa_enabled = models.BooleanField(default=False, help_text="Whether MFA is enabled for this user")
    mfa_required = models.BooleanField(default=False, help_text="Whether MFA is required (set automatically for VIP/Premium)")
    mfa_setup_completed = models.BooleanField(default=False, help_text="Whether user has completed MFA setup")
    mfa_setup_date = models.DateTimeField(null=True, blank=True, help_text="When MFA was first set up")
    
    # NDPR Compliance Fields
    data_processing_consent = models.BooleanField(default=False)
    data_processing_consent_date = models.DateTimeField(null=True, blank=True)
    marketing_consent = models.BooleanField(default=False)
    marketing_consent_date = models.DateTimeField(null=True, blank=True)
    location_tracking_consent = models.BooleanField(default=False)
    location_tracking_consent_date = models.DateTimeField(null=True, blank=True)
    data_retention_period_years = models.PositiveIntegerField(default=7)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_location_lat = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True
    )
    last_location_lng = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True
    )
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # Custom manager
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['user_type']),
            models.Index(fields=['tier']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.email} ({self.get_user_type_display()})'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
    
    def enable_mfa_for_tier(self, save=True):
        """
        Automatically enable MFA requirement based on user tier.
        Called when user is upgraded to VIP or VIP Premium.
        """
        if self.tier in [UserTier.VIP, UserTier.VIP_PREMIUM]:
            self.mfa_required = True
            if not self.mfa_enabled:
                self.mfa_enabled = True
            if save:
                self.save(update_fields=['mfa_required', 'mfa_enabled'])
    
    def setup_mfa_completed(self, save=True):
        """Mark MFA setup as completed"""
        from django.utils import timezone
        self.mfa_setup_completed = True
        if not self.mfa_setup_date:
            self.mfa_setup_date = timezone.now()
        if save:
            self.save(update_fields=['mfa_setup_completed', 'mfa_setup_date'])
    
    @property
    def needs_mfa_setup(self):
        """Check if user needs to complete MFA setup"""
        return self.mfa_required and not self.mfa_setup_completed
    
    @property
    def has_active_mfa_methods(self):
        """Check if user has any active MFA methods configured"""
        return self.mfa_tokens.filter(is_active=True).exists()

    def can_access_tier(self, required_tier):
        """Check if user can access a specific tier service"""
        tier_hierarchy = {
            UserTier.NORMAL: 1,
            UserTier.VIP: 2,  # Now VIP is the lower paid tier
            UserTier.VIP_PREMIUM: 3,  # VIP Premium is the highest
        }
        user_level = tier_hierarchy.get(self.tier, 0)
        required_level = tier_hierarchy.get(required_tier, 0)
        return user_level >= required_level


class Driver(models.Model):
    """Enhanced Driver model with categories and compliance"""
    
    class SubscriptionTier(models.TextChoices):
        BASIC = 'basic', 'Basic ($99/month)'
        PREMIUM = 'premium', 'Premium ($199/month)'
        VIP = 'vip', 'VIP ($299/month)'
    
    class DriverStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Verification'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        INACTIVE = 'inactive', 'Inactive'
        REJECTED = 'rejected', 'Rejected'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )
    
    # Driver Category
    category = models.CharField(
        max_length=20,
        choices=DriverCategory.choices,
        default=DriverCategory.PRIVATE
    )
    
    # License Information
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry_date = models.DateField()
    license_class = models.CharField(max_length=10, default='C')
    
    # Subscription
    subscription_tier = models.CharField(
        max_length=10,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.BASIC
    )
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    subscription_auto_renew = models.BooleanField(default=True)
    
    # Status and Verification
    status = models.CharField(
        max_length=10,
        choices=DriverStatus.choices,
        default=DriverStatus.PENDING
    )
    
    # Documents
    license_front_image = models.ImageField(upload_to='driver_docs/licenses/')
    license_back_image = models.ImageField(upload_to='driver_docs/licenses/')
    identity_document = models.ImageField(upload_to='driver_docs/identity/')
    proof_of_address = models.ImageField(upload_to='driver_docs/address/')
    background_check_document = models.FileField(
        upload_to='driver_docs/background/',
        null=True,
        blank=True
    )
    
    # Background Check
    background_check_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('expired', 'Expired'),
        ],
        default='pending'
    )
    background_check_date = models.DateTimeField(null=True, blank=True)
    background_check_expiry = models.DateTimeField(null=True, blank=True)
    
    # Financial Information
    bank_account_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_code = models.CharField(max_length=10, blank=True)
    tax_identification_number = models.CharField(max_length=50, blank=True)
    
    # Fleet Association (for fleet employees)
    fleet_company = models.ForeignKey(
        'fleet_management.FleetCompany',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers'
    )
    fleet_employee_id = models.CharField(max_length=50, blank=True)
    
    # Performance Metrics
    total_rides = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00
    )
    cancellation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    # Real-time Status
    is_online = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    current_location_lat = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True
    )
    current_location_lng = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True
    )
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drivers'
        indexes = [
            models.Index(fields=['license_number']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['subscription_tier']),
            models.Index(fields=['is_online', 'is_available']),
            models.Index(fields=['fleet_company']),
            models.Index(fields=['average_rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.get_category_display()}'
    
    @property
    def is_subscription_active(self):
        """Check if driver's subscription is currently active"""
        from django.utils import timezone
        if not self.subscription_end_date:
            return False
        return self.subscription_end_date > timezone.now()
    
    def can_accept_tier_rides(self, tier):
        """Check if driver can accept rides for a specific tier"""
        tier_access = {
            self.SubscriptionTier.BASIC: [UserTier.NORMAL],
            self.SubscriptionTier.PREMIUM: [
                UserTier.NORMAL, 
                UserTier.PREMIUM
            ],
            self.SubscriptionTier.VIP: [
                UserTier.NORMAL, 
                UserTier.PREMIUM, 
                UserTier.VIP
            ],
        }
        return tier in tier_access.get(self.subscription_tier, [])
    
    @property
    def can_drive_premium_vehicles(self):
        """Check if driver can drive premium vehicles"""
        return self.subscription_tier in [
            self.SubscriptionTier.PREMIUM,
            self.SubscriptionTier.VIP
        ]


# Authentication and Security Models

class UserSession(models.Model):
    """Track user sessions for security and concurrent session management"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sessions'
    )
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Device information
    device_fingerprint = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    
    # Location information
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    
    # Session management
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    # Security flags
    is_trusted_device = models.BooleanField(default=False)
    requires_mfa = models.BooleanField(default=False)
    mfa_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_id']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.email} - {self.session_id[:8]}"


class TrustedDevice(models.Model):
    """Manage trusted devices for users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='trusted_devices'
    )
    device_fingerprint = models.CharField(max_length=64, db_index=True)
    
    # Device information
    device_name = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    
    # Trust settings
    is_active = models.BooleanField(default=True)
    trust_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Trust'),
            ('high', 'High Trust'),
            ('vip', 'VIP Trust'),
        ],
        default='basic'
    )
    
    # Usage tracking
    first_used_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trusted_devices'
        unique_together = ['user', 'device_fingerprint']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_fingerprint']),
            models.Index(fields=['last_used_at']),
        ]
    
    def __str__(self):
        device_name = self.device_name or 'Unnamed'
        return f"Trusted device for {self.user.email} - {device_name}"


class MFAToken(models.Model):
    """Multi-Factor Authentication tokens and settings"""
    
    TOKEN_TYPES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('totp', 'TOTP App'),
        ('backup', 'Backup Code'),
        ('biometric', 'Biometric'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='mfa_tokens'
    )
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    
    # Token data (encrypted in production)
    secret_key = models.CharField(max_length=255, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email_address = models.EmailField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    
    # Usage tracking
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Failure tracking
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mfa_tokens'
        unique_together = ['user', 'token_type']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token_type']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        return f"MFA {self.token_type} for {self.user.email}"
    
    def generate_totp_secret(self):
        """Generate TOTP secret key"""
        if self.token_type == 'totp':
            import pyotp
            self.secret_key = pyotp.random_base32()
            self.save()
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code generation"""
        if self.token_type == 'totp' and self.secret_key:
            import pyotp
            return pyotp.totp.TOTP(self.secret_key).provisioning_uri(
                name=self.user.email,
                issuer_name="VIP Ride Platform"
            )
        return None
    
    def verify_totp(self, token: str) -> bool:
        """Verify TOTP token"""
        if self.token_type != 'totp' or not self.secret_key:
            return False
        
        import pyotp
        from django.utils import timezone
        from datetime import timedelta
        
        totp = pyotp.TOTP(self.secret_key)
        is_valid = totp.verify(token, valid_window=1)  # Allow 30s window
        
        if is_valid:
            self.last_used_at = timezone.now()
            self.usage_count += 1
            self.failed_attempts = 0
            self.save()
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.locked_until = timezone.now() + timedelta(minutes=15)
            self.save()
        
        return is_valid
    
    def verify_backup_code(self, code: str) -> bool:
        """Verify backup code"""
        if self.token_type != 'backup' or code not in self.backup_codes:
            return False
        
        from django.utils import timezone
        
        # Remove used backup code
        self.backup_codes.remove(code)
        self.last_used_at = timezone.now()
        self.usage_count += 1
        self.save()
        
        return True
    
    def generate_backup_codes(self, count: int = 10):
        """Generate new backup codes"""
        if self.token_type == 'backup':
            import secrets
            codes = []
            for _ in range(count):
                code = secrets.token_hex(4).upper()
                codes.append(code)
            self.backup_codes = codes
            self.save()
            return codes
        return []
    
    def is_locked(self) -> bool:
        """Check if MFA token is locked due to failed attempts"""
        from django.utils import timezone
        return self.locked_until and timezone.now() < self.locked_until


class LoginAttempt(models.Model):
    """Track login attempts for security monitoring"""
    
    ATTEMPT_TYPES = [
        ('success', 'Successful Login'),
        ('failed_password', 'Failed Password'),
        ('failed_mfa', 'Failed MFA'),
        ('blocked_suspicious', 'Blocked Suspicious'),
        ('blocked_rate_limit', 'Blocked Rate Limit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_attempts', 
        null=True, 
        blank=True
    )
    email = models.EmailField()
    
    # Attempt details
    attempt_type = models.CharField(max_length=20, choices=ATTEMPT_TYPES)
    success = models.BooleanField(default=False)
    
    # Device and location information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=64, blank=True)
    
    # Location (from IP geolocation)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Additional security info
    is_suspicious = models.BooleanField(default=False)
    risk_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    blocked_reason = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'login_attempts'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['success', 'created_at']),
            models.Index(fields=['is_suspicious']),
        ]
    
    def __str__(self):
        return f"Login attempt by {self.email} - {self.attempt_type}"


class SecurityEvent(models.Model):
    """Track security events and incidents"""
    
    EVENT_TYPES = [
        ('suspicious_login', 'Suspicious Login'),
        ('multiple_failed_logins', 'Multiple Failed Logins'),
        ('unusual_location', 'Unusual Location'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('mfa_bypass_attempt', 'MFA Bypass Attempt'),
        ('token_manipulation', 'Token Manipulation'),
        ('concurrent_session_abuse', 'Concurrent Session Abuse'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='security_events', 
        null=True, 
        blank=True
    )
    
    # Event details
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    description = models.TextField()
    
    # Context information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Response tracking
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resolved_events'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Automated response
    auto_response_taken = models.CharField(max_length=100, blank=True)
    manual_review_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_events'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['event_type', 'severity']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Security Event: {self.event_type} - {self.severity}"


# Import Premium Card models
from .premium_card_models import PremiumDigitalCard, PremiumCardTransaction

# Import Activation History models  
from .activation_history_models import CardActivationHistory, CardUsageLog
