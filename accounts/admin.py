"""
Django Admin Configuration for Accounts App
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from .models import (
    User, Driver, UserSession, TrustedDevice, 
    MFAToken, LoginAttempt, SecurityEvent
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced admin for User model"""
    
    list_display = [
        'email', 'username', 'full_name', 'tier', 'user_type',
        'is_active', 'is_email_verified', 'date_joined'
    ]
    list_filter = [
        'tier', 'user_type', 'is_active', 'is_email_verified',
        'is_staff', 'is_superuser', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    readonly_fields = ['id', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')
        }),
        ('User Classification', {
            'fields': ('tier', 'user_type', 'is_email_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Privacy & Consent', {
            'fields': (
                'location_tracking_consent', 'location_tracking_consent_date',
                'data_processing_consent', 'marketing_consent'
            ),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'tier', 'user_type'),
        }),
    )
    
    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email
    full_name.short_description = 'Full Name'


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Admin for Driver model"""
    
    list_display = [
        'user_info', 'category', 'subscription_tier', 'status',
        'average_rating', 'total_rides', 'background_check_status', 'license_expiry_date'
    ]
    list_filter = [
        'category', 'subscription_tier', 'status', 'background_check_status',
        'license_expiry_date', 'background_check_status'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'license_number', 'vehicle_registration'
    ]
    readonly_fields = [
        'id', 'total_rides', 'total_earnings', 'average_rating',
        'background_check_date', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Driver Information', {
            'fields': ('user', 'category', 'subscription_tier', 'status')
        }),
        ('License & Verification', {
            'fields': (
                'license_number', 'license_class', 'license_expiry_date',
                'background_check_status', 'background_check_date'
            )
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_registration', 'vehicle_make', 'vehicle_model', 'vehicle_year')
        }),
        ('Performance Metrics', {
            'fields': ('average_rating', 'total_rides', 'total_earnings'),
            'classes': ('collapse',)
        }),
        ('Bank Information', {
            'fields': ('bank_name', 'bank_account_number', 'bank_account_name'),
            'classes': ('collapse',)
        }),
        ('Working Preferences', {
            'fields': ('preferred_zones', 'max_working_hours', 'preferred_vehicle_types'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_info(self, obj):
        """Display user information"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:accounts_user_change', args=[obj.user.id]),
            obj.user.email
        )
    user_info.short_description = 'User'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin for User Sessions"""
    
    list_display = [
        'user', 'ip_address', 'is_active', 'location_display',
        'created_at', 'last_activity', 'session_duration'
    ]
    list_filter = [
        'is_active', 'created_at', 'last_activity'
    ]
    search_fields = ['user__email', 'ip_address', 'user_agent']
    readonly_fields = [
        'id', 'session_id', 'created_at', 'last_activity', 'session_duration'
    ]
    
    def location_display(self, obj):
        """Display location info"""
        return f"{obj.city}, {obj.country}" if obj.city else "-"
    location_display.short_description = 'Location'
    
    def session_duration(self, obj):
        """Calculate session duration"""
        if obj.last_activity and obj.created_at:
            duration = obj.last_activity - obj.created_at
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        return "-"
    session_duration.short_description = 'Duration'


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    """Admin for Trusted Devices"""
    
    list_display = [
        'user', 'device_name', 'trust_level', 'is_active',
        'last_used_at', 'usage_count', 'created_at'
    ]
    list_filter = [
        'trust_level', 'is_active', 'created_at', 'last_used_at'
    ]
    search_fields = ['user__email', 'device_name', 'device_fingerprint']
    readonly_fields = ['id', 'device_fingerprint', 'created_at', 'last_used_at']


@admin.register(MFAToken)
class MFATokenAdmin(admin.ModelAdmin):
    """Admin for MFA Tokens"""
    
    list_display = [
        'user', 'token_type', 'is_active', 'is_expired',
        'created_at', 'last_used_at', 'usage_count'
    ]
    list_filter = [
        'token_type', 'is_active', 'created_at', 'last_used_at'
    ]
    search_fields = ['user__email']
    readonly_fields = [
        'id', 'secret_key', 'created_at', 'last_used_at'
    ]
    
    def is_expired(self, obj):
        """Check if token is locked"""
        return obj.locked_until and obj.locked_until > timezone.now()
    is_expired.boolean = True
    is_expired.short_description = 'Locked'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin for Login Attempts"""
    
    list_display = [
        'email', 'success', 'ip_address',
        'user_agent_short', 'created_at', 'blocked_reason'
    ]
    list_filter = [
        'success', 'created_at', 'blocked_reason'
    ]
    search_fields = ['email', 'ip_address']
    readonly_fields = [
        'id', 'email', 'ip_address', 'user_agent',
        'created_at', 'success', 'blocked_reason', 'attempt_type'
    ]
    
    def user_agent_short(self, obj):
        """Display shortened user agent"""
        return obj.user_agent[:50] + "..." if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_short.short_description = 'User Agent'
    
    def has_add_permission(self, request):
        """Prevent manual creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent modification"""
        return False


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """Admin for Security Events"""
    
    list_display = [
        'user', 'event_type', 'severity', 'ip_address',
        'created_at', 'is_resolved', 'description_short'
    ]
    list_filter = [
        'event_type', 'severity', 'is_resolved', 'created_at'
    ]
    search_fields = ['user__email', 'event_type', 'description']
    readonly_fields = [
        'id', 'user', 'event_type', 'severity', 'ip_address',
        'user_agent', 'created_at', 'description', 'session_id'
    ]
    
    def description_short(self, obj):
        """Display shortened description"""
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    def has_add_permission(self, request):
        """Prevent manual creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow only resolution updates"""
        return True


# Admin site customization
admin.site.site_header = "VIP Ride-Hailing Platform - Accounts Management"
admin.site.site_title = "Accounts Admin"
admin.site.index_title = "Accounts Management Dashboard"
