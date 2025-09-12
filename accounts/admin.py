"""
Django Admin Configuration for Accounts App
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse, path
from .models import (
    User, Driver, UserSession, TrustedDevice, 
    MFAToken, LoginAttempt, SecurityEvent
)
from .premium_card_models import PremiumDigitalCard, PremiumCardTransaction
from .premium_card_batch_models import PremiumCardBatchGeneration

# Import the batch admin to ensure it's registered
from . import premium_card_batch_admin


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
    search_fields = [
        'email', 'username', 'first_name', 'last_name', 'phone_number'
    ]
    readonly_fields = ['id', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'date_of_birth'
            )
        }),
        ('User Classification', {
            'fields': ('tier', 'user_type', 'is_email_verified')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Privacy & Consent', {
            'fields': (
                'location_tracking_consent', 'location_tracking_consent_date',
                'data_processing_consent', 'marketing_consent'
            ),
            'classes': ('collapse',)
        }),
    # Emergency contact is on Driver model, not User
        ('Important Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'phone_number', 'password1', 'password2',
                'tier', 'user_type'
            ),
        }),
    )
    
    @admin.display(description='Full Name')
    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Admin for Driver model"""
    
    list_display = [
        'user_info', 'category', 'subscription_tier', 'status',
        'average_rating', 'total_rides', 'background_check_status',
        'license_expiry_date'
    ]
    list_filter = [
        'category', 'subscription_tier', 'status', 'background_check_status',
        'license_expiry_date'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'license_number'
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
        ('Performance Metrics', {
            'fields': ('average_rating', 'total_rides', 'total_earnings'),
            'classes': ('collapse',)
        }),
        ('Bank Information', {
            'fields': (
                'bank_name', 'bank_account_number', 'bank_account_name'
            ),
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
    readonly_fields = [
        'id', 'device_fingerprint', 'created_at', 'last_used_at'
    ]


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
    
    @admin.display(boolean=True, description='Locked')
    def is_expired(self, obj):
        """Check if token is locked"""
        return obj.locked_until and obj.locked_until > timezone.now()


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
    
    @admin.display(description='User Agent')
    def user_agent_short(self, obj):
        """Display shortened user agent"""
        if obj.user_agent and len(obj.user_agent) > 50:
            return obj.user_agent[:50] + "..."
        return obj.user_agent
    
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
    
    @admin.display(description='Description')
    def description_short(self, obj):
        """Display shortened description"""
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + "..."
        return obj.description
    
    def has_add_permission(self, request):
        """Prevent manual creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow only resolution updates"""
        return True


# VIP Card Admin Registration
try:
    from .vip_card_admin import (
        VIPDigitalCardAdmin, CardActivationHistoryAdmin, CardBatchGenerationAdmin
    )
    from .vip_card_models import (
        VIPDigitalCard, CardActivationHistory, CardBatchGeneration
    )
    
    # Remove the @admin.register decorators and register manually
    admin.site.register(VIPDigitalCard, VIPDigitalCardAdmin)
    admin.site.register(CardActivationHistory, CardActivationHistoryAdmin)
    admin.site.register(CardBatchGeneration, CardBatchGenerationAdmin)
    
except ImportError as e:
    # VIP card admin not available yet
    pass
except Exception as e:
    # Handle other registration errors
    print(f"VIP card admin registration error: {e}")


# Admin site customization
admin.site.site_header = "VIP Ride-Hailing Platform - Accounts Management"
admin.site.site_title = "Accounts Admin"
admin.site.index_title = "Accounts Management Dashboard"


# Premium Digital Card Admin
@admin.register(PremiumDigitalCard)
class PremiumDigitalCardAdmin(admin.ModelAdmin):
    """Admin interface for Premium Digital Cards"""
    
    list_display = [
        'card_number',
        'tier',
        'status',
        'owner',
        'price',
        'purchased_at',
        'activated_at',
        'expires_at'
    ]
    
    list_filter = [
        'tier',
        'status',
        'created_at',
        'purchased_at',
        'activated_at'
    ]
    
    search_fields = [
        'card_number',
        'verification_code',
        'owner__email',
        'owner__first_name',
        'owner__last_name'
    ]
    
    readonly_fields = [
        'id',
        'card_number',
        'verification_code',
        'created_at',
        'activated_at',
        'activation_ip'
    ]
    
    fieldsets = [
        ('Card Information', {
            'fields': [
                'id',
                'card_number',
                'verification_code',
                'tier',
                'status'
            ]
        }),
        ('Pricing & Validity', {
            'fields': [
                'price',
                'validity_months'
            ]
        }),
        ('Ownership', {
            'fields': [
                'owner'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'purchased_at',
                'activated_at',
                'expires_at'
            ]
        }),
        ('Metadata', {
            'fields': [
                'purchase_transaction_id',
                'activation_ip'
            ]
        })
    ]
    
    def get_urls(self):
        """Add custom URLs for batch operations"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-batch/',
                self.admin_site.admin_view(self.generate_batch_redirect),
                name='accounts_premiumdigitalcard_generate_batch'
            ),
        ]
        return custom_urls + urls
    
    def generate_batch_redirect(self, request):
        """Redirect to batch generation admin"""
        from django.shortcuts import redirect
        return redirect('/admin/accounts/premiumcardbatchgeneration/generate-batch/')
    
    def changelist_view(self, request, extra_context=None):
        """Add batch generation button to changelist"""
        extra_context = extra_context or {}
        extra_context['show_generate_batch_button'] = True
        return super().changelist_view(request, extra_context)
    
    def get_inlines(self, request, obj):
        """Add activation history inline for existing cards"""
        inlines = []
        if obj and obj.pk:  # Only show for existing cards
            from .activation_history_admin import CardActivationHistoryInline, CardUsageLogInline
            # Filter inlines to show only premium card history
            class PremiumCardActivationHistoryInline(CardActivationHistoryInline):
                def get_queryset(self, request):
                    qs = super().get_queryset(request)
                    return qs.filter(card_type='premium')
            
            class PremiumCardUsageLogInline(CardUsageLogInline):
                def get_queryset(self, request):
                    qs = super().get_queryset(request)
                    return qs.filter(premium_card__isnull=False)
            
            inlines.extend([PremiumCardActivationHistoryInline, PremiumCardUsageLogInline])
        return inlines


@admin.register(PremiumCardTransaction)
class PremiumCardTransactionAdmin(admin.ModelAdmin):
    """Admin interface for Premium Card Transactions"""
    
    list_display = [
        'id',
        'card',
        'user',
        'amount',
        'currency',
        'status',
        'payment_method',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'currency',
        'created_at'
    ]
    
    search_fields = [
        'id',
        'card__card_number',
        'user__email',
        'payment_reference'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'completed_at'
    ]
