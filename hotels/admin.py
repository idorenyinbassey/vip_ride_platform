"""
Django Admin Configuration for Hotels App
"""

from django.contrib import admin
from .models import HotelPartner, HotelRoom, HotelBooking


@admin.register(HotelPartner)
class HotelPartnerAdmin(admin.ModelAdmin):
    """Admin for Hotel Partners"""
    
    list_display = [
        'name', 'category', 'partnership_tier', 'city',
        'total_rooms', 'commission_rate', 'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'partnership_tier', 'is_active',
        'city', 'state', 'created_at'
    ]
    search_fields = ['name', 'email', 'phone', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    """Admin for Hotel Rooms"""
    
    list_display = [
        'hotel', 'room_number', 'room_type', 'max_occupancy',
        'base_price_per_night', 'is_available', 'created_at'
    ]
    list_filter = [
        'room_type', 'is_available', 'max_occupancy', 'created_at'
    ]
    search_fields = ['hotel__name', 'room_number', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    """Admin for Hotel Bookings"""
    
    list_display = [
        'customer', 'hotel', 'room', 'status',
        'check_in_date', 'check_out_date', 'total_amount', 'booked_at'
    ]
    list_filter = [
        'status', 'booked_at', 'check_in_date'
    ]
    search_fields = ['customer__email', 'hotel__name', 'primary_guest_name']
    readonly_fields = [
        'id', 'booked_at', 'created_at', 'updated_at'
    ]
