"""
Django Admin Configuration for Vehicle Leasing App
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import VehicleLease, LeasePayment


@admin.register(VehicleLease)
class VehicleLeaseAdmin(admin.ModelAdmin):
    """Admin for Vehicle Lease model"""
    
    list_display = [
        'vehicle', 'vehicle_owner', 'fleet_company', 'status',
        'start_date', 'end_date'
    ]
    list_filter = [
        'status', 'start_date', 'end_date', 'created_at'
    ]
    search_fields = [
        'vehicle__license_plate', 'vehicle_owner__email'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
# Admin site customization
admin.site.site_header = "VIP Ride-Hailing Platform - Vehicle Leasing"
admin.site.site_title = "Vehicle Leasing Admin"
admin.site.index_title = "Vehicle Leasing Dashboard"
