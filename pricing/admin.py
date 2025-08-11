"""
VIP Ride-Hailing Platform - Pricing Admin Interface
Django admin configuration for pricing management

NOTE: Currently using simplified coordinate system for development.
TODO: When going full scale production, consider upgrading to GeoDjango 
for more precise geographic boundaries and advanced spatial features.
This will require:
1. Installing PostGIS for PostgreSQL
2. Updating models to use PolygonField for zones
3. Updating admin to use OSMGeoAdmin
4. More complex zone boundary definitions
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    PricingZone, TimeBasedPricing, SpecialEvent, DemandSurge,
    PromotionalCode, PricingRule, PriceCalculationLog
)


@admin.register(PricingZone)
class PricingZoneAdmin(admin.ModelAdmin):
    """Admin interface for pricing zones with map display"""
    list_display = [
        'name', 'city', 'base_multiplier', 'is_premium_zone',
        'surge_enabled', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_premium_zone', 'surge_enabled',
        'city', 'created_at'
    ]
    search_fields = ['name', 'description', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'city', 'country')
        }),
        ('Geographic Boundary', {
            'fields': (
                'min_latitude', 'max_latitude', 
                'min_longitude', 'max_longitude'
            ),
            'classes': ('wide',)
        }),
        ('Pricing Configuration', {
            'fields': (
                'base_multiplier', 'is_premium_zone',
                'surge_enabled', 'max_surge_multiplier'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(TimeBasedPricing)
class TimeBasedPricingAdmin(admin.ModelAdmin):
    """Admin interface for time-based pricing rules"""
    list_display = [
        'name', 'day_of_week', 'start_time', 'end_time',
        'multiplier', 'priority', 'is_active'
    ]
    list_filter = [
        'is_active', 'day_of_week', 'priority'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('name', 'description', 'priority')
        }),
        ('Time Schedule', {
            'fields': (
                'day_of_week', 'start_time', 'end_time',
                'date_from', 'date_until'
            )
        }),
        ('Pricing Multipliers', {
            'fields': (
                'multiplier', 'normal_tier_multiplier',
                'premium_tier_multiplier', 'vip_tier_multiplier'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )


@admin.register(SpecialEvent)
class SpecialEventAdmin(admin.ModelAdmin):
    """Admin interface for special event pricing"""
    list_display = [
        'name', 'event_type', 'start_datetime', 'end_datetime',
        'base_multiplier', 'is_active'
    ]
    list_filter = [
        'is_active', 'event_type', 'start_datetime'
    ]
    search_fields = ['name', 'description', 'venue_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'name', 'description', 'event_type',
                'venue_name', 'organizer'
            )
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'affected_zones'),
            'classes': ('wide',)
        }),
        ('Pricing', {
            'fields': (
                'base_multiplier', 'peak_multiplier',
                'peak_start_offset', 'peak_end_offset'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )
    
    filter_horizontal = ['affected_zones']


@admin.register(DemandSurge)
class DemandSurgeAdmin(admin.ModelAdmin):
    """Admin interface for demand surge monitoring"""
    list_display = [
        'zone', 'surge_level', 'surge_multiplier', 'demand_ratio',
        'calculated_at', 'expires_at', 'is_active'
    ]
    list_filter = [
        'is_active', 'surge_level', 'zone', 'calculated_at'
    ]
    search_fields = ['zone__name']
    readonly_fields = [
        'calculated_at', 'updated_at', 'demand_ratio',
        'surge_level', 'surge_multiplier'
    ]
    
    fieldsets = (
        ('Zone Information', {
            'fields': ('zone',)
        }),
        ('Demand Metrics', {
            'fields': (
                'active_rides', 'pending_requests',
                'available_drivers', 'demand_ratio'
            )
        }),
        ('Surge Calculation', {
            'fields': ('surge_level', 'surge_multiplier')
        }),
        ('Validity', {
            'fields': ('is_active', 'calculated_at', 'expires_at', 'updated_at')
        })
    )
    
    def has_add_permission(self, request):
        # Surge records are created automatically
        return False


@admin.register(PromotionalCode)
class PromotionalCodeAdmin(admin.ModelAdmin):
    """Admin interface for promotional codes"""
    list_display = [
        'code', 'code_type', 'discount_type', 'discount_value',
        'usage_count', 'max_uses', 'is_active', 'expires_at'
    ]
    list_filter = [
        'is_active', 'code_type', 'discount_type',
        'eligible_tiers', 'created_at'
    ]
    search_fields = ['code', 'description']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Code Information', {
            'fields': ('code', 'description', 'code_type')
        }),
        ('Discount Settings', {
            'fields': (
                'discount_type', 'discount_value',
                'minimum_trip_amount', 'maximum_discount'
            )
        }),
        ('Usage Limits', {
            'fields': (
                'max_uses', 'max_uses_per_user',
                'usage_count', 'first_ride_only'
            )
        }),
        ('Eligibility', {
            'fields': (
                'eligible_tiers', 'applies_to_surge',
                'valid_from', 'expires_at'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    """Admin interface for pricing rules"""
    list_display = [
        'vehicle_type', 'zone', 'base_fare', 'per_km_rate',
        'per_minute_rate', 'is_active', 'effective_from'
    ]
    list_filter = [
        'is_active', 'vehicle_type', 'zone', 'effective_from'
    ]
    search_fields = ['vehicle_type', 'zone__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Rule Configuration', {
            'fields': ('vehicle_type', 'zone')
        }),
        ('Base Pricing', {
            'fields': (
                'base_fare', 'per_km_rate', 'per_minute_rate',
                'minimum_fare', 'booking_fee'
            )
        }),
        ('Tier Multipliers', {
            'fields': (
                'normal_multiplier', 'premium_multiplier',
                'vip_multiplier'
            )
        }),
        ('Effective Period', {
            'fields': ('effective_from', 'effective_until')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )


@admin.register(PriceCalculationLog)
class PriceCalculationLogAdmin(admin.ModelAdmin):
    """Admin interface for price calculation logs"""
    list_display = [
        'user', 'vehicle_type', 'final_price', 'surge_multiplier',
        'promo_discount_display', 'created_at'
    ]
    list_filter = [
        'vehicle_type', 'created_at', 'surge_multiplier'
    ]
    search_fields = ['user__email', 'applied_promo_code']
    readonly_fields = [
        'user', 'pickup_latitude', 'pickup_longitude',
        'dropoff_latitude', 'dropoff_longitude', 'distance_km',
        'estimated_duration_minutes', 'vehicle_type', 'base_fare',
        'distance_fare', 'time_fare', 'subtotal', 'zone_multiplier',
        'time_multiplier', 'surge_multiplier', 'event_multiplier',
        'tier_multiplier', 'total_before_discount', 'promo_discount',
        'final_price', 'applied_promo_code', 'pricing_factors', 'created_at'
    ]
    
    fieldsets = (
        ('Trip Information', {
            'fields': (
                'user', 'pickup_latitude', 'pickup_longitude',
                'dropoff_latitude', 'dropoff_longitude',
                'distance_km', 'estimated_duration_minutes', 'vehicle_type'
            )
        }),
        ('Base Calculation', {
            'fields': ('base_fare', 'distance_fare', 'time_fare', 'subtotal')
        }),
        ('Pricing Multipliers', {
            'fields': (
                'zone_multiplier', 'time_multiplier', 'surge_multiplier',
                'event_multiplier', 'tier_multiplier'
            )
        }),
        ('Final Pricing', {
            'fields': (
                'total_before_discount', 'promo_discount',
                'final_price', 'applied_promo_code'
            )
        }),
        ('Metadata', {
            'fields': ('pricing_factors', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def promo_discount_display(self, obj):
        """Display promo discount with formatting"""
        if obj.promo_discount:
            return format_html(
                '<span style="color: green;">-₦{}</span>',
                obj.promo_discount
            )
        return '-'
    
    def has_add_permission(self, request):
        # Logs are created automatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Logs should not be modified
        return False


# Admin site customization
admin.site.site_header = "VIP Ride-Hailing Platform - Pricing Management"
admin.site.site_title = "Pricing Admin"
admin.site.index_title = "Pricing Management Dashboard"
