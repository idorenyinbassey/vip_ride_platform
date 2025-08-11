"""
Django Admin Configuration for Fleet Management App
"""

from django.contrib import admin
from .models import Vehicle, FleetCompany


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Vehicle Admin"""
    
    list_display = [
        'license_plate', 'make', 'model', 'year', 'owner', 'category',
        'engine_type', 'status', 'ownership_status', 'created_at'
    ]
    
    list_filter = [
        'category', 'engine_type', 'status', 'ownership_status',
        'fuel_type', 'has_air_conditioning', 'has_gps',
        'comprehensive_insurance', 'created_at'
    ]
    
    search_fields = [
        'license_plate', 'vin_number', 'make', 'model',
        'owner__email', 'owner__first_name', 'owner__last_name'
    ]
    
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': (
                'owner', 'make', 'model', 'year', 'color',
                'license_plate', 'vin_number', 'registration_number'
            )
        }),
        ('Category & Engine', {
            'fields': (
                'category', 'engine_type', 'engine_displacement',
                'fuel_type', 'fuel_consumption_per_km'
            )
        }),
        ('Capacity', {
            'fields': ('passenger_capacity', 'luggage_capacity')
        }),
        ('Features', {
            'fields': (
                'has_air_conditioning', 'has_gps', 'has_wifi',
                'has_baby_seat', 'has_wheelchair_access', 'has_luxury_interior'
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'ownership_status')
        }),
        ('Insurance', {
            'fields': (
                'insurance_policy_number', 'insurance_expiry_date',
                'comprehensive_insurance', 'road_worthiness_expiry'
            )
        }),
        ('Documents', {
            'fields': (
                'registration_document', 'insurance_document',
                'road_worthiness_certificate'
            ),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': (
                'front_image', 'back_image', 'interior_image', 'side_image'
            ),
            'classes': ('collapse',)
        }),
        ('Maintenance', {
            'fields': (
                'current_mileage', 'maintenance_interval_km',
                'last_maintenance_date', 'next_maintenance_date'
            )
        }),
        ('Financial', {
            'fields': ('purchase_price', 'current_market_value'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FleetCompany)
class FleetCompanyAdmin(admin.ModelAdmin):
    """Fleet Company Admin"""
    
    list_display = [
        'company_name', 'owner', 'company_size', 'is_verified',
        'is_active', 'total_vehicles', 'created_at'
    ]
    
    list_filter = [
        'company_size', 'is_verified', 'is_active', 'verification_level',
        'offers_premium_vehicles', 'offers_luxury_vehicles',
        'offers_vip_services', 'created_at'
    ]
    
    search_fields = [
        'company_name', 'company_registration_number', 'tax_id',
        'business_email', 'owner__email'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'verification_date',
        'total_vehicles', 'active_vehicles', 'premium_vehicles'
    ]
    
    fieldsets = (
        ('Company Info', {
            'fields': (
                'owner', 'company_name', 'company_registration_number',
                'tax_id', 'company_size'
            )
        }),
        ('Contact', {
            'fields': (
                'business_address', 'business_phone', 'business_email',
                'website'
            )
        }),
        ('Services', {
            'fields': (
                'offers_premium_vehicles', 'offers_luxury_vehicles',
                'offers_vip_services', 'priority_vip_allocation'
            )
        }),
        ('Operations', {
            'fields': ('operational_cities',)
        }),
        ('Verification', {
            'fields': (
                'is_verified', 'verification_level', 'verification_date',
                'is_active'
            )
        }),
        ('Billing', {
            'fields': (
                'fixed_rate_per_km', 'premium_rate_multiplier',
                'platform_commission_rate', 'driver_commission_rate'
            )
        }),
        ('Statistics', {
            'fields': (
                'total_vehicles', 'active_vehicles', 'premium_vehicles',
                'monthly_revenue', 'average_rating'
            ),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
