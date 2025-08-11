"""
VIP Ride-Hailing Platform - Pricing Serializers
Django REST Framework serializers for pricing API
"""

from rest_framework import serializers
from decimal import Decimal
from .models import PricingZone, PromotionalCode


class PriceQuoteRequestSerializer(serializers.Serializer):
    """Serializer for price quote request"""
    pickup_lat = serializers.FloatField(
        min_value=-90.0, max_value=90.0,
        help_text="Pickup latitude"
    )
    pickup_lng = serializers.FloatField(
        min_value=-180.0, max_value=180.0,
        help_text="Pickup longitude"
    )
    dropoff_lat = serializers.FloatField(
        min_value=-90.0, max_value=90.0,
        help_text="Drop-off latitude"
    )
    dropoff_lng = serializers.FloatField(
        min_value=-180.0, max_value=180.0,
        help_text="Drop-off longitude"
    )
    distance_km = serializers.DecimalField(
        max_digits=8, decimal_places=2,
        min_value=Decimal('0.1'), max_value=Decimal('999.99'),
        help_text="Distance in kilometers"
    )
    estimated_duration_minutes = serializers.IntegerField(
        min_value=1, max_value=999,
        help_text="Estimated trip duration in minutes"
    )
    vehicle_type = serializers.ChoiceField(
        choices=[
            ('economy', 'Economy'),
            ('comfort', 'Comfort'),
            ('premium', 'Premium'),
            ('luxury', 'Luxury'),
            ('suv', 'SUV'),
            ('van', 'Van')
        ],
        help_text="Type of vehicle requested"
    )
    promo_code = serializers.CharField(
        max_length=20, required=False, allow_blank=True,
        help_text="Optional promotional code"
    )


class PricingBreakdownSerializer(serializers.Serializer):
    """Serializer for detailed pricing breakdown"""
    base_fare = serializers.DecimalField(max_digits=10, decimal_places=2)
    zone_multiplier = serializers.DecimalField(max_digits=5, decimal_places=3)
    time_multiplier = serializers.DecimalField(max_digits=5, decimal_places=3)
    surge_multiplier = serializers.DecimalField(max_digits=5, decimal_places=3)
    event_multiplier = serializers.DecimalField(max_digits=5, decimal_places=3)
    tier_multiplier = serializers.DecimalField(max_digits=5, decimal_places=3)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    promo_discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    minimum_fare = serializers.DecimalField(max_digits=10, decimal_places=2)
    booking_fee = serializers.DecimalField(max_digits=10, decimal_places=2)


class PricingFactorSerializer(serializers.Serializer):
    """Serializer for individual pricing factors"""
    factor = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=200)
    multiplier = serializers.DecimalField(
        max_digits=5, decimal_places=3, required=False
    )
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    icon = serializers.CharField(max_length=20, required=False)


class TransparencyInfoSerializer(serializers.Serializer):
    """Serializer for pricing transparency information"""
    pricing_factors = PricingFactorSerializer(many=True)
    user_friendly_explanation = serializers.ListField(
        child=serializers.CharField(max_length=200)
    )


class PriceQuoteResponseSerializer(serializers.Serializer):
    """Serializer for price quote response"""
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    surge_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pricing_breakdown = PricingBreakdownSerializer()
    transparency_info = TransparencyInfoSerializer()
    calculation_log = serializers.DictField(required=False)


class SurgeLevelSerializer(serializers.Serializer):
    """Serializer for surge level information"""
    zone_name = serializers.CharField(max_length=100)
    surge_level = serializers.CharField(max_length=20)
    multiplier = serializers.DecimalField(max_digits=5, decimal_places=3)
    demand_ratio = serializers.DecimalField(max_digits=8, decimal_places=3)


class PricingZoneSerializer(serializers.ModelSerializer):
    """Serializer for pricing zone information"""
    
    class Meta:
        model = PricingZone
        fields = [
            'id', 'name', 'description', 'base_multiplier',
            'is_premium_zone', 'surge_enabled', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PromotionalCodeValidationSerializer(serializers.Serializer):
    """Serializer for promotional code validation"""
    valid = serializers.BooleanField()
    code = serializers.CharField(max_length=20, required=False)
    description = serializers.CharField(max_length=200, required=False)
    discount_type = serializers.CharField(max_length=20, required=False)
    discount_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    applies_to_surge = serializers.BooleanField(required=False)
    reason = serializers.CharField(max_length=200, required=False)
