"""
Vehicle Leasing serializers
"""

from rest_framework import serializers
from .models import VehicleLease, LeasePayment
from fleet_management.models import Vehicle


class VehicleLeaseSerializer(serializers.ModelSerializer):
    """Vehicle lease serializer"""
    
    class Meta:
        model = VehicleLease
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class LeasePaymentSerializer(serializers.ModelSerializer):
    """Lease payment serializer"""
    
    class Meta:
        model = LeasePayment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


# Placeholder serializers for compatibility with views
class VehicleListingSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle model for listing purposes"""
    
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'license_plate', 
                 'color', 'category', 'engine_type', 'passenger_capacity',
                 'status', 'owner']
        read_only_fields = ['id', 'owner']


class LeaseContractSerializer(serializers.ModelSerializer):
    """Alias for VehicleLeaseSerializer"""
    
    class Meta:
        model = VehicleLease
        fields = '__all__'


class VehicleOwnerSerializer(serializers.Serializer):
    """Placeholder vehicle owner serializer"""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()


class RevenueReportSerializer(serializers.Serializer):
    """Placeholder revenue report serializer"""
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


class LeaseCalculationSerializer(serializers.Serializer):
    """Lease calculation input serializer"""
    vehicle_id = serializers.UUIDField()
    revenue_share_model = serializers.CharField()
    vehicle_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    lease_duration = serializers.IntegerField()
    down_payment = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    interest_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8.5
    )
    expected_monthly_rides = serializers.IntegerField(default=100)
    average_ride_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2500
    )
    fixed_monthly_payment = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    revenue_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False
    )
    per_ride_commission = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )


class VehicleSearchSerializer(serializers.Serializer):
    """Vehicle search parameters serializer"""
    vehicle_type = serializers.CharField(required=False)
    brand = serializers.CharField(required=False)
    fuel_type = serializers.CharField(required=False)
    transmission = serializers.CharField(required=False)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    max_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    location = serializers.CharField(required=False)
