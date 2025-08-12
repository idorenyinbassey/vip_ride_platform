from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class VehicleLease(models.Model):
    """Enhanced vehicle lease model with revenue sharing"""
    
    class LeaseStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        EXPIRED = 'expired', 'Expired'
        TERMINATED = 'terminated', 'Terminated'
        CANCELLED = 'cancelled', 'Cancelled'
    
    class RevenueShareModel(models.TextChoices):
        FIXED_MONTHLY = 'fixed_monthly', 'Fixed Monthly Payment'
        PERCENTAGE_REVENUE = 'percentage_revenue', 'Percentage of Revenue'
        HYBRID = 'hybrid', 'Hybrid (Fixed + Percentage)'
        PER_RIDE = 'per_ride', 'Per Ride Commission'
    
    class MaintenanceResponsibility(models.TextChoices):
        OWNER = 'owner', 'Vehicle Owner'
        FLEET = 'fleet', 'Fleet Company'
        SHARED = 'shared', 'Shared Responsibility'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Parties
    vehicle_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lease_contracts_as_owner'
    )
    fleet_company = models.ForeignKey(
        'fleet_management.FleetCompany',
        on_delete=models.CASCADE,
        related_name='lease_contracts'
    )
    vehicle = models.ForeignKey(
        'fleet_management.Vehicle',
        on_delete=models.CASCADE,
        related_name='lease_contracts'
    )
    
    # Contract Terms
    start_date = models.DateField()
    end_date = models.DateField()
    auto_renewal = models.BooleanField(default=False)
    renewal_period_months = models.PositiveIntegerField(default=12)
    
    status = models.CharField(
        max_length=20,
        choices=LeaseStatus.choices,
        default=LeaseStatus.DRAFT
    )
    
    # Revenue Sharing Model
    revenue_share_model = models.CharField(
        max_length=20,
        choices=RevenueShareModel.choices,
        default=RevenueShareModel.PERCENTAGE_REVENUE
    )
    
    # Financial Terms
    fixed_monthly_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Fixed monthly lease payment to vehicle owner'
    )
    revenue_share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage of ride revenue shared with vehicle owner'
    )
    per_ride_commission = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text='Fixed commission per completed ride'
    )
    minimum_monthly_guarantee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Minimum guaranteed monthly payment to owner'
    )
    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Operating Conditions
    maximum_daily_hours = models.PositiveIntegerField(
        default=12,
        help_text='Maximum operating hours per day'
    )
    maximum_monthly_mileage = models.PositiveIntegerField(
        default=5000,
        help_text='Maximum mileage per month'
    )
    allowed_service_areas = models.TextField(
        help_text='Comma-separated list of allowed service areas'
    )
    
    # Responsibilities
    maintenance_responsibility = models.CharField(
        max_length=10,
        choices=MaintenanceResponsibility.choices,
        default=MaintenanceResponsibility.FLEET
    )
    insurance_responsibility = models.CharField(
        max_length=10,
        choices=MaintenanceResponsibility.choices,
        default=MaintenanceResponsibility.FLEET
    )
    fuel_responsibility = models.CharField(
        max_length=10,
        choices=MaintenanceResponsibility.choices,
        default=MaintenanceResponsibility.FLEET
    )
    
    # Performance Metrics
    total_rides_completed = models.PositiveIntegerField(default=0)
    total_revenue_generated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    total_owner_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    total_fleet_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    average_daily_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Mileage Tracking
    start_mileage = models.PositiveIntegerField(default=0)
    current_mileage = models.PositiveIntegerField(default=0)
    excess_mileage_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.50,
        help_text='Rate per km for excess mileage'
    )
    
    # Contract Documents
    contract_document = models.FileField(upload_to='contracts/')
    vehicle_handover_checklist = models.FileField(
        upload_to='contracts/handover/',
        null=True,
        blank=True
    )
    signed_date = models.DateTimeField(null=True, blank=True)
    owner_signature = models.ImageField(
        upload_to='contracts/signatures/',
        null=True,
        blank=True
    )
    fleet_signature = models.ImageField(
        upload_to='contracts/signatures/',
        null=True,
        blank=True
    )
    
    # Termination
    termination_notice_period_days = models.PositiveIntegerField(default=30)
    early_termination_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    termination_date = models.DateTimeField(null=True, blank=True)
    termination_reason = models.TextField(blank=True)
    
    # NDPR Compliance
    data_sharing_consent = models.BooleanField(default=False)
    data_sharing_consent_date = models.DateTimeField(null=True, blank=True)
    performance_data_retention_days = models.PositiveIntegerField(default=2555)  # 7 years
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicle_leases'
        indexes = [
            models.Index(fields=['vehicle_owner']),
            models.Index(fields=['fleet_company']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['revenue_share_model']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [
            ['vehicle', 'fleet_company', 'start_date'],
        ]
    
    def __str__(self):
        return f'Lease: {self.vehicle} to {self.fleet_company.company_name}'
    
    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == self.LeaseStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date:
            return (self.end_date - timezone.now().date()).days
        return 0
    
    def calculate_owner_payment(self, period_revenue=0, rides_completed=0):
        """Calculate payment to vehicle owner based on revenue share model"""
        payment = 0
        
        if self.revenue_share_model == self.RevenueShareModel.FIXED_MONTHLY:
            payment = self.fixed_monthly_payment
        
        elif self.revenue_share_model == self.RevenueShareModel.PERCENTAGE_REVENUE:
            payment = period_revenue * (self.revenue_share_percentage / 100)
        
        elif self.revenue_share_model == self.RevenueShareModel.HYBRID:
            percentage_payment = period_revenue * (self.revenue_share_percentage / 100)
            payment = self.fixed_monthly_payment + percentage_payment
        
        elif self.revenue_share_model == self.RevenueShareModel.PER_RIDE:
            payment = rides_completed * self.per_ride_commission
        
        # Apply minimum guarantee if applicable
        if self.minimum_monthly_guarantee > 0:
            payment = max(payment, self.minimum_monthly_guarantee)
        
        return payment
    
    def calculate_excess_mileage_charges(self):
        """Calculate charges for excess mileage"""
        if self.current_mileage <= self.start_mileage:
            return 0
        
        total_mileage = self.current_mileage - self.start_mileage
        months_active = self.get_active_months()
        
        if months_active == 0:
            return 0
        
        allowed_mileage = self.maximum_monthly_mileage * months_active
        excess_mileage = max(0, total_mileage - allowed_mileage)
        
        return excess_mileage * self.excess_mileage_rate
    
    def get_active_months(self):
        """Calculate number of active months"""
        from django.utils import timezone
        
        if not self.is_active:
            return 0
        
        start = max(self.start_date, timezone.now().date().replace(day=1))
        end = min(self.end_date, timezone.now().date())
        
        months = (end.year - start.year) * 12 + (end.month - start.month)
        return max(1, months)


class LeasePayment(models.Model):
    """Track payments made to vehicle owners"""
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    lease = models.ForeignKey(
        VehicleLease,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Payment Period
    payment_period_start = models.DateField()
    payment_period_end = models.DateField()
    
    # Payment Details
    base_payment = models.DecimalField(max_digits=10, decimal_places=2)
    revenue_share_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    excess_mileage_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    maintenance_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    damage_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Performance Data
    rides_completed = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_mileage = models.PositiveIntegerField(default=0)
    
    # Payment Processing
    status = models.CharField(
        max_length=15,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lease_payments'
        indexes = [
            models.Index(fields=['lease']),
            models.Index(fields=['payment_period_start', 'payment_period_end']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
        ]
        unique_together = [
            ['lease', 'payment_period_start', 'payment_period_end'],
        ]
    
    def __str__(self):
        return f'Payment {self.payment_period_start} - {self.lease.vehicle}'
