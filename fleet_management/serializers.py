"""
Fleet Management Serializers
Secure serializers for fleet and vehicle management
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

from .models import (
    Vehicle, FleetCompany, VehicleCategory, EngineType
)

User = get_user_model()


class VehicleSerializer(serializers.ModelSerializer):
    """Vehicle serializer with security validations"""
    
    owner_name = serializers.CharField(
        source='owner.get_full_name', read_only=True
    )
    is_available = serializers.ReadOnlyField()
    is_premium_vehicle = serializers.ReadOnlyField()
    flexible_billing_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'owner_name', 'make', 'model', 'year',
            'license_plate', 'vin_number', 'color', 'category', 'engine_type',
            'engine_displacement', 'ownership_status', 'passenger_capacity',
            'luggage_capacity', 'status', 'registration_number',
            'insurance_policy_number', 'insurance_expiry_date',
            'road_worthiness_expiry', 'comprehensive_insurance',
            'front_image', 'back_image', 'interior_image', 'side_image',
            'fuel_consumption_per_km', 'fuel_type', 'has_air_conditioning',
            'has_gps', 'has_wifi', 'has_baby_seat', 'has_wheelchair_access',
            'has_luxury_interior', 'has_partition', 'has_premium_sound',
            'current_mileage', 'last_mileage_update', 'last_maintenance_date',
            'next_maintenance_date', 'maintenance_interval_km',
            'purchase_price', 'current_market_value', 'is_available',
            'is_premium_vehicle', 'flexible_billing_rate', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'owner_name', 'is_available', 'is_premium_vehicle',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'vin_number': {'write_only': True},  # Sensitive information
            'registration_document': {'write_only': True},
            'insurance_document': {'write_only': True},
            'purchase_price': {'write_only': True},
        }
    
    def get_flexible_billing_rate(self, obj):
        """Get calculated billing rate"""
        return obj.calculate_flexible_billing_rate()
    
    def validate_license_plate(self, value):
        """Validate license plate format"""
        # Basic validation - adjust based on your region
        if not re.match(r'^[A-Z0-9-]{3,10}$', value.upper()):
            raise serializers.ValidationError(
                "Invalid license plate format"
            )
        return value.upper()
    
    def validate_vin_number(self, value):
        """Validate VIN number"""
        if len(value) != 17:
            raise serializers.ValidationError(
                "VIN number must be exactly 17 characters"
            )
        if not re.match(r'^[A-HJ-NPR-Z0-9]+$', value.upper()):
            raise serializers.ValidationError(
                "Invalid VIN number format"
            )
        return value.upper()
    
    def validate_year(self, value):
        """Validate vehicle year"""
        from datetime import datetime
        current_year = datetime.now().year
        
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Vehicle year must be between 1900 and {current_year + 1}"
            )
        return value
    
    def validate_fuel_consumption_per_km(self, value):
        """Validate fuel consumption"""
        if value <= 0 or value > 50:
            raise serializers.ValidationError(
                "Fuel consumption must be between 0.01 and 50.00 L/km"
            )
        return value
    
    def validate_passenger_capacity(self, value):
        """Validate passenger capacity"""
        if value < 1 or value > 50:
            raise serializers.ValidationError(
                "Passenger capacity must be between 1 and 50"
            )
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Check insurance expiry
        insurance_expiry = attrs.get('insurance_expiry_date')
        road_worthiness_expiry = attrs.get('road_worthiness_expiry')
        
        if insurance_expiry and road_worthiness_expiry:
            from datetime import datetime
            today = datetime.now().date()
            
            if insurance_expiry <= today:
                raise serializers.ValidationError({
                    'insurance_expiry_date': 'Insurance must not be expired'
                })
            
            if road_worthiness_expiry <= today:
                raise serializers.ValidationError({
                    'road_worthiness_expiry':
                        'Road worthiness certificate must not be expired'
                })
        
        # Validate category and engine type combination
        category = attrs.get('category')
        engine_type = attrs.get('engine_type')
        
        luxury_engines = [EngineType.V6, EngineType.V8]
        if (category == VehicleCategory.LUXURY and
                engine_type not in luxury_engines):
            raise serializers.ValidationError({
                'engine_type': 'Luxury vehicles must have V6 or V8 engines'
            })
        
        return attrs


class VehicleCreateSerializer(VehicleSerializer):
    """Serializer for vehicle creation with additional validations"""
    
    def create(self, validated_data):
        """Create vehicle with owner assignment"""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class VehicleUpdateSerializer(serializers.ModelSerializer):
    """Limited serializer for vehicle updates"""
    
    class Meta:
        model = Vehicle
        fields = [
            'status', 'current_mileage', 'last_maintenance_date',
            'next_maintenance_date', 'current_market_value',
            'has_air_conditioning', 'has_wifi', 'has_baby_seat',
            'has_wheelchair_access', 'has_partition', 'has_premium_sound'
        ]
    
    def validate_current_mileage(self, value):
        """Validate mileage increase"""
        if self.instance and value < self.instance.current_mileage:
            raise serializers.ValidationError(
                "Mileage cannot be decreased"
            )
        return value


class FleetCompanySerializer(serializers.ModelSerializer):
    """Fleet company serializer with security validations"""
    
    owner_name = serializers.CharField(
        source='owner.get_full_name', read_only=True
    )
    utilization_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = FleetCompany
        fields = [
            'id', 'owner', 'owner_name', 'company_name',
            'company_registration_number', 'tax_id', 'company_size',
            'business_address', 'business_phone', 'business_email',
            'website', 'offers_premium_vehicles', 'offers_luxury_vehicles',
            'offers_vip_services', 'priority_vip_allocation',
            'operational_cities', 'airport_service_available',
            'hotel_partnership_eligible', 'is_verified', 'is_active',
            'verification_date', 'verification_level',
            'fixed_rate_per_km', 'premium_rate_multiplier',
            'vip_rate_multiplier', 'platform_commission_rate',
            'driver_commission_rate', 'total_vehicles', 'active_vehicles',
            'premium_vehicles', 'total_drivers', 'active_drivers',
            'monthly_revenue', 'total_rides_completed', 'average_rating',
            'utilization_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner_name', 'is_verified', 'verification_date',
            'total_vehicles', 'active_vehicles', 'premium_vehicles',
            'total_drivers', 'active_drivers', 'monthly_revenue',
            'total_rides_completed', 'average_rating', 'utilization_rate',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'tax_id': {'write_only': True},
            'business_license': {'write_only': True},
            'tax_certificate': {'write_only': True},
            'insurance_certificate': {'write_only': True},
        }
    
    def validate_company_registration_number(self, value):
        """Validate company registration number"""
        if not re.match(r'^[A-Z0-9-]{5,20}$', value.upper()):
            raise serializers.ValidationError(
                "Invalid company registration number format"
            )
        return value.upper()
    
    def validate_tax_id(self, value):
        """Validate tax ID"""
        if not re.match(r'^[A-Z0-9-]{5,20}$', value.upper()):
            raise serializers.ValidationError(
                "Invalid tax ID format"
            )
        return value.upper()
    
    def validate_business_phone(self, value):
        """Validate business phone"""
        if not re.match(r'^\+?[\d\s\-\(\)]{10,20}$', value):
            raise serializers.ValidationError(
                "Invalid phone number format"
            )
        return value
    
    def validate_fixed_rate_per_km(self, value):
        """Validate fixed rate"""
        if value <= 0 or value > 1000:
            raise serializers.ValidationError(
                "Fixed rate must be between 0.01 and 1000.00"
            )
        return value
    
    def validate_platform_commission_rate(self, value):
        """Validate commission rate"""
        if value < 5 or value > 30:
            raise serializers.ValidationError(
                "Platform commission must be between 5% and 30%"
            )
        return value
    
    def validate_driver_commission_rate(self, value):
        """Validate driver commission rate"""
        if value < 50 or value > 90:
            raise serializers.ValidationError(
                "Driver commission must be between 50% and 90%"
            )
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        platform_commission = attrs.get('platform_commission_rate', 0)
        driver_commission = attrs.get('driver_commission_rate', 0)
        
        if platform_commission + driver_commission > 95:
            raise serializers.ValidationError(
                "Total commission rates cannot exceed 95%"
            )
        
        return attrs


class FleetCompanyCreateSerializer(FleetCompanySerializer):
    """Serializer for fleet company creation"""
    
    def create(self, validated_data):
        """Create fleet company with owner assignment"""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class FleetAnalyticsSerializer(serializers.Serializer):
    """Serializer for fleet analytics data"""
    
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rides = serializers.IntegerField()
    monthly_rides = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    utilization_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    top_vehicles = serializers.ListField(child=serializers.DictField())
    revenue_trends = serializers.ListField(child=serializers.DictField())
    maintenance_alerts = serializers.ListField(child=serializers.DictField())


class VehicleAssignmentSerializer(serializers.Serializer):
    """Serializer for vehicle-driver assignments"""
    
    vehicle_id = serializers.UUIDField()
    driver_id = serializers.UUIDField()
    assignment_type = serializers.ChoiceField(
        choices=[
            ('permanent', 'Permanent Assignment'),
            ('temporary', 'Temporary Assignment'),
            ('rotation', 'Rotation Assignment')
        ]
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(
        max_length=500, required=False, allow_blank=True
    )
    
    def validate(self, attrs):
        """Validate assignment dates"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        return attrs


class MaintenanceRecordSerializer(serializers.Serializer):
    """Serializer for vehicle maintenance records"""
    
    vehicle_id = serializers.UUIDField()
    maintenance_type = serializers.ChoiceField(
        choices=[
            ('routine', 'Routine Maintenance'),
            ('repair', 'Repair'),
            ('inspection', 'Inspection'),
            ('emergency', 'Emergency Repair')
        ]
    )
    description = serializers.CharField(max_length=1000)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    service_provider = serializers.CharField(max_length=200)
    maintenance_date = serializers.DateField()
    next_maintenance_date = serializers.DateField(
        required=False, allow_null=True
    )
    mileage_at_service = serializers.IntegerField()
    
    def validate_cost(self, value):
        """Validate maintenance cost"""
        if value <= 0:
            raise serializers.ValidationError(
                "Maintenance cost must be greater than 0"
            )
        return value
    
    def validate_mileage_at_service(self, value):
        """Validate mileage"""
        if value < 0:
            raise serializers.ValidationError(
                "Mileage cannot be negative"
            )
        return value
