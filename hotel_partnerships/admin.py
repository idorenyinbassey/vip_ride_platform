from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Hotel, HotelStaff, HotelRoom, HotelGuest, HotelBooking,
    HotelCommissionReport, BulkBookingEvent, PMSIntegrationLog
)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'tier', 'status', 'city', 'commission_rate',
        'total_rooms', 'pms_type', 'booking_count', 'created_at'
    ]
    list_filter = [
        'status', 'tier', 'pms_type', 'city', 'state',
        'auto_assign_rides', 'guest_booking_enabled'
    ]
    search_fields = ['name', 'brand', 'email', 'phone', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'brand', 'tier', 'status', 'star_rating', 'total_rooms'
            )
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'state', 'country', 
                'latitude', 'longitude'
            )
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Partnership Terms', {
            'fields': (
                'commission_rate', 'minimum_monthly_bookings',
                'preferred_vehicle_types'
            )
        }),
        ('PMS Integration', {
            'fields': (
                'pms_type', 'pms_endpoint', 'pms_api_key',
                'pms_webhook_secret'
            ),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': (
                'auto_assign_rides', 'send_real_time_updates',
                'allow_bulk_bookings', 'guest_booking_enabled'
            )
        }),
        ('Audit', {
            'fields': ('id', 'created_at', 'updated_at', 'onboarded_by'),
            'classes': ('collapse',)
        })
    )
    
    def booking_count(self, obj):
        """Show total bookings for this hotel"""
        count = len(obj.bookings.all())
        url = reverse('admin:hotel_partnerships_hotelbooking_changelist')
        return format_html(
            '<a href="{}?hotel__id__exact={}">{} bookings</a>',
            url, obj.id, count
        )
    booking_count.short_description = 'Bookings'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('bookings')


@admin.register(HotelStaff)
class HotelStaffAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'hotel', 'role', 'permission_level', 'department',
        'is_active', 'last_login', 'created_at'
    ]
    list_filter = [
        'role', 'permission_level', 'is_active', 'hotel__tier',
        'hotel__status'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'hotel__name', 'employee_id', 'phone'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    fieldsets = (
        ('User & Hotel', {
            'fields': ('user', 'hotel')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'permission_level', 'department', 'employee_id')
        }),
        ('Contact', {
            'fields': ('phone', 'extension')
        }),
        ('Access Control', {
            'fields': (
                'is_active', 'last_login', 'login_attempts', 'locked_until'
            )
        }),
        ('Audit', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = [
        'hotel', 'room_number', 'room_type', 'floor', 'capacity',
        'status', 'base_rate'
    ]
    list_filter = ['hotel', 'room_type', 'status', 'has_balcony']
    search_fields = ['hotel__name', 'room_number']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(HotelGuest)
class HotelGuestAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'hotel', 'room', 'guest_type',
        'check_in_date', 'check_out_date', 'is_checked_in', 'is_vip'
    ]
    list_filter = [
        'hotel', 'guest_type', 'is_checked_in', 'is_vip',
        'check_in_date', 'check_out_date'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'phone',
        'pms_guest_id', 'loyalty_number'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Guest Name'


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference', 'hotel', 'guest_name', 'booking_type',
        'pickup_datetime', 'status', 'final_fare', 'hotel_commission',
        'created_at'
    ]
    list_filter = [
        'hotel', 'booking_type', 'status', 'priority', 'vehicle_type',
        'pickup_datetime'
    ]
    search_fields = [
        'booking_reference', 'guest_name', 'guest_phone',
        'guest_room_number', 'pickup_location', 'destination'
    ]
    readonly_fields = [
        'id', 'booking_reference', 'created_at', 'updated_at',
        'completed_at', 'last_update_sent'
    ]
    
    fieldsets = (
        ('Booking Information', {
            'fields': (
                'booking_reference', 'hotel', 'guest', 'booked_by_staff',
                'booking_type', 'priority'
            )
        }),
        ('Guest Details', {
            'fields': (
                'guest_name', 'guest_phone', 'guest_room_number',
                'passenger_count'
            )
        }),
        ('Trip Details', {
            'fields': (
                'pickup_location', 'pickup_latitude', 'pickup_longitude',
                'destination', 'destination_latitude', 'destination_longitude',
                'pickup_datetime', 'estimated_duration'
            )
        }),
        ('Service Requirements', {
            'fields': ('vehicle_type', 'special_instructions')
        }),
        ('Pricing & Commission', {
            'fields': (
                'estimated_fare', 'final_fare', 'hotel_commission',
                'commission_rate_used'
            )
        }),
        ('Status & Tracking', {
            'fields': (
                'status', 'ride_id', 'driver_assigned', 'status_updates'
            )
        }),
        ('Event Booking', {
            'fields': ('event_name', 'bulk_booking_group'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': (
                'id', 'created_at', 'updated_at', 'completed_at',
                'last_update_sent'
            ),
            'classes': ('collapse',)
        })
    )
    
    def commission_percentage(self, obj):
        """Display commission as percentage"""
        if obj.commission_rate_used:
            return f"{obj.commission_rate_used}%"
        return "-"
    commission_percentage.short_description = 'Commission %'


@admin.register(HotelCommissionReport)
class HotelCommissionReportAdmin(admin.ModelAdmin):
    list_display = [
        'hotel', 'report_month', 'total_bookings', 'completed_bookings',
        'total_commission_earned', 'status', 'payment_due_date'
    ]
    list_filter = [
        'hotel', 'status', 'report_month', 'payment_due_date'
    ]
    search_fields = ['hotel__name', 'payment_reference']
    readonly_fields = ['id', 'generated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('hotel', 'report_month', 'status')
        }),
        ('Booking Metrics', {
            'fields': (
                'total_bookings', 'completed_bookings', 'cancelled_bookings'
            )
        }),
        ('Financial Summary', {
            'fields': (
                'total_ride_value', 'total_commission_earned',
                'average_commission_rate'
            )
        }),
        ('Performance', {
            'fields': ('average_rating', 'response_time_avg')
        }),
        ('Payment Details', {
            'fields': (
                'payment_due_date', 'payment_made_date', 'payment_reference'
            )
        }),
        ('Detailed Data', {
            'fields': ('detailed_data',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('id', 'generated_at', 'generated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(BulkBookingEvent)
class BulkBookingEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_name', 'hotel', 'event_type', 'event_date',
        'expected_guests', 'estimated_rides', 'status'
    ]
    list_filter = ['hotel', 'event_type', 'status', 'event_date']
    search_fields = [
        'event_name', 'description', 'event_coordinator_name',
        'event_coordinator_email'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'event_name', 'event_type', 'description', 'hotel', 'status'
            )
        }),
        ('Schedule', {
            'fields': ('event_date', 'start_time', 'end_time')
        }),
        ('Logistics', {
            'fields': (
                'expected_guests', 'pickup_locations', 'destination_venue',
                'estimated_rides', 'vehicle_types_needed', 'special_requirements'
            )
        }),
        ('Coordination', {
            'fields': (
                'event_coordinator_name', 'event_coordinator_phone',
                'event_coordinator_email'
            )
        }),
        ('Costs', {
            'fields': ('estimated_total_cost', 'actual_total_cost')
        }),
        ('Audit', {
            'fields': ('id', 'created_at', 'created_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(PMSIntegrationLog)
class PMSIntegrationLogAdmin(admin.ModelAdmin):
    list_display = [
        'hotel', 'action_type', 'success', 'booking_reference',
        'pms_reference', 'created_at', 'processing_time'
    ]
    list_filter = [
        'hotel', 'action_type', 'success', 'created_at'
    ]
    search_fields = [
        'hotel__name', 'booking_reference', 'pms_reference',
        'error_message'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Log Information', {
            'fields': (
                'hotel', 'action_type', 'success', 'booking_reference',
                'pms_reference'
            )
        }),
        ('Request/Response Data', {
            'fields': ('request_data', 'response_data', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('id', 'created_at', 'processing_time'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        """Prevent manual addition of logs"""
        return False
