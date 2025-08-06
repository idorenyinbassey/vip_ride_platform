from django.db import models
from django.conf import settings
import uuid


class VehicleCategory(models.TextChoices):
    CLASSIC = 'CLASSIC', 'Classic Car'
    PREMIUM = 'PREMIUM', 'Premium Car'
    VAN = 'VAN', 'Van'
    LUXURY = 'LUXURY', 'Luxury Car'


class EngineType(models.TextChoices):
    V6 = 'V6', 'V6 Engine'
    V8 = 'V8', 'V8 Engine'
    FOUR_STROKE = '4_stroke', '4-Stroke Engine'
    ELECTRIC = 'electric', 'Electric'
    HYBRID = 'hybrid', 'Hybrid'


class VehicleStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    MAINTENANCE = 'maintenance', 'Under Maintenance'
    INACTIVE = 'inactive', 'Inactive'
    RETIRED = 'retired', 'Retired'


class OwnershipStatus(models.TextChoices):
    OWNED = 'owned', 'Owned'
    LEASED_TO_FLEET = 'leased_to_fleet', 'Leased to Fleet'
    FLEET_OWNED = 'fleet_owned', 'Fleet Owned'
    FINANCING = 'financing', 'Under Financing'


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Owner Information
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_vehicles'
    )
    
    # Vehicle Details
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    vin_number = models.CharField(max_length=17, unique=True)
    color = models.CharField(max_length=30)
    
    # Category and Engine
    category = models.CharField(
        max_length=10,
        choices=VehicleCategory.choices,
        default=VehicleCategory.CLASSIC
    )
    engine_type = models.CharField(
        max_length=15,
        choices=EngineType.choices,
        default=EngineType.FOUR_STROKE
    )
    engine_displacement = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Engine displacement in liters'
    )
    
    # Ownership
    ownership_status = models.CharField(
        max_length=20,
        choices=OwnershipStatus.choices,
        default=OwnershipStatus.OWNED
    )
    
    # Capacity
    passenger_capacity = models.PositiveIntegerField(default=4)
    luggage_capacity = models.CharField(max_length=50, blank=True)
    
    # Status
    status = models.CharField(
        max_length=12,
        choices=VehicleStatus.choices,
        default=VehicleStatus.ACTIVE
    )
    
    # Registration and Insurance
    registration_number = models.CharField(max_length=50)
    insurance_policy_number = models.CharField(max_length=50)
    insurance_expiry_date = models.DateField()
    road_worthiness_expiry = models.DateField()
    comprehensive_insurance = models.BooleanField(default=True)
    
    # Images
    front_image = models.ImageField(upload_to='vehicles/images/')
    back_image = models.ImageField(upload_to='vehicles/images/')
    interior_image = models.ImageField(upload_to='vehicles/images/')
    side_image = models.ImageField(
        upload_to='vehicles/images/',
        null=True,
        blank=True
    )
    
    # Documents
    registration_document = models.FileField(upload_to='vehicles/documents/')
    insurance_document = models.FileField(upload_to='vehicles/documents/')
    road_worthiness_certificate = models.FileField(
        upload_to='vehicles/documents/',
        null=True,
        blank=True
    )
    
    # Fuel Consumption (for flexible billing)
    fuel_consumption_per_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Liters per kilometer'
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=[
            ('petrol', 'Petrol/Gasoline'),
            ('diesel', 'Diesel'),
            ('electric', 'Electric'),
            ('hybrid', 'Hybrid'),
            ('lpg', 'LPG'),
        ],
        default='petrol'
    )
    
    # Premium Features
    has_air_conditioning = models.BooleanField(default=True)
    has_gps = models.BooleanField(default=True)
    has_wifi = models.BooleanField(default=False)
    has_baby_seat = models.BooleanField(default=False)
    has_wheelchair_access = models.BooleanField(default=False)
    has_luxury_interior = models.BooleanField(default=False)
    has_partition = models.BooleanField(default=False)
    has_premium_sound = models.BooleanField(default=False)
    
    # Mileage
    current_mileage = models.PositiveIntegerField(default=0)
    last_mileage_update = models.DateTimeField(null=True, blank=True)
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_interval_km = models.PositiveIntegerField(default=10000)
    
    # Financial Information
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    current_market_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicles'
        indexes = [
            models.Index(fields=['license_plate']),
            models.Index(fields=['vin_number']),
            models.Index(fields=['owner']),
            models.Index(fields=['category']),
            models.Index(fields=['engine_type']),
            models.Index(fields=['ownership_status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.year} {self.make} {self.model} - {self.license_plate}'
    
    @property
    def is_available(self):
        return self.status == VehicleStatus.ACTIVE
    
    @property
    def is_premium_vehicle(self):
        """Check if vehicle qualifies as premium"""
        return (
            self.category in [VehicleCategory.PREMIUM, VehicleCategory.LUXURY] or
            self.engine_type in [EngineType.V6, EngineType.V8] or
            self.has_luxury_interior
        )
    
    def calculate_flexible_billing_rate(self):
        """Calculate billing rate based on engine type and consumption"""
        base_rates = {
            EngineType.FOUR_STROKE: 2.0,
            EngineType.V6: 3.5,
            EngineType.V8: 5.0,
            EngineType.ELECTRIC: 1.5,
            EngineType.HYBRID: 2.5,
        }
        
        base_rate = base_rates.get(self.engine_type, 2.0)
        consumption_factor = float(self.fuel_consumption_per_km) * 0.5
        
        return base_rate + consumption_factor


class FleetCompany(models.Model):
    """Enhanced Fleet Company with premium vehicle management"""
    
    class CompanySize(models.TextChoices):
        SMALL = 'small', 'Small (1-10 vehicles)'
        MEDIUM = 'medium', 'Medium (11-50 vehicles)'
        LARGE = 'large', 'Large (51-200 vehicles)'
        ENTERPRISE = 'enterprise', 'Enterprise (200+ vehicles)'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Company Information
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fleet_companies'
    )
    company_name = models.CharField(max_length=200)
    company_registration_number = models.CharField(max_length=50, unique=True)
    tax_id = models.CharField(max_length=50, unique=True)
    company_size = models.CharField(
        max_length=15,
        choices=CompanySize.choices,
        default=CompanySize.SMALL
    )
    
    # Contact Information
    business_address = models.TextField()
    business_phone = models.CharField(max_length=20)
    business_email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Premium Services
    offers_premium_vehicles = models.BooleanField(default=True)
    offers_luxury_vehicles = models.BooleanField(default=False)
    offers_vip_services = models.BooleanField(default=False)
    priority_vip_allocation = models.BooleanField(default=True)
    
    # Operational Areas
    operational_cities = models.TextField(
        help_text='Comma-separated list of cities'
    )
    airport_service_available = models.BooleanField(default=False)
    hotel_partnership_eligible = models.BooleanField(default=True)
    
    # Documents
    business_license = models.FileField(upload_to='fleet_docs/licenses/')
    tax_certificate = models.FileField(upload_to='fleet_docs/tax/')
    insurance_certificate = models.FileField(upload_to='fleet_docs/insurance/')
    fleet_insurance_policy = models.FileField(
        upload_to='fleet_docs/fleet_insurance/',
        null=True,
        blank=True
    )
    
    # Status and Verification
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Verification'),
            ('premium', 'Premium Verification'),
            ('enterprise', 'Enterprise Verification'),
        ],
        default='basic'
    )
    
    # Billing Configuration
    fixed_rate_per_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='Fixed rate per kilometer for fleet vehicles'
    )
    premium_rate_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.5,
        help_text='Multiplier for premium vehicle rates'
    )
    vip_rate_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.0,
        help_text='Multiplier for VIP service rates'
    )
    
    # Commission Structure
    platform_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        help_text='Platform commission percentage'
    )
    driver_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        help_text='Driver commission percentage'
    )
    
    # Statistics
    total_vehicles = models.PositiveIntegerField(default=0)
    active_vehicles = models.PositiveIntegerField(default=0)
    premium_vehicles = models.PositiveIntegerField(default=0)
    total_drivers = models.PositiveIntegerField(default=0)
    active_drivers = models.PositiveIntegerField(default=0)
    
    # Financial
    monthly_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    total_rides_completed = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fleet_companies'
        verbose_name_plural = 'Fleet Companies'
        indexes = [
            models.Index(fields=['company_registration_number']),
            models.Index(fields=['is_verified', 'is_active']),
            models.Index(fields=['verification_level']),
            models.Index(fields=['company_size']),
            models.Index(fields=['offers_premium_vehicles']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.company_name
    
    @property
    def utilization_rate(self):
        """Calculate fleet utilization rate"""
        if self.total_vehicles == 0:
            return 0
        return (self.active_vehicles / self.total_vehicles) * 100
