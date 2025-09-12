"""
Admin configuration for Card Activation History
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .activation_history_models import CardActivationHistory, CardUsageLog


@admin.register(CardActivationHistory)
class CardActivationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'card_identifier_display',
        'card_type',
        'user_email',
        'status',
        'attempted_at',
        'completed_at',
        'activation_method',
        'ip_address',
        'duration_display'
    ]
    
    list_filter = [
        'status',
        'card_type',
        'activation_method',
        'attempted_at',
        ('completed_at', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'user__email',
        'user__name',
        'vip_card__serial_number',
        'premium_card__card_number',
        'ip_address',
        'activation_code_used'
    ]
    
    readonly_fields = [
        'id',
        'attempted_at',
        'completed_at',
        'duration_display',
        'card_link'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('card_type', 'card_link', 'user', 'status')
        }),
        ('Activation Details', {
            'fields': ('activation_method', 'activation_code_used', 'admin_user')
        }),
        ('Network Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('attempted_at', 'completed_at', 'duration_display')
        }),
        ('Additional Information', {
            'fields': ('error_message', 'notes'),
            'classes': ('collapse',)
        })
    )
    
    def card_identifier_display(self, obj):
        """Display card identifier with link"""
        if obj.vip_card:
            url = reverse('admin:accounts_vipdigitalcard_change', args=[obj.vip_card.pk])
            return format_html('<a href="{}">{}</a>', url, obj.vip_card.serial_number)
        elif obj.premium_card:
            url = reverse('admin:accounts_premiumdigitalcard_change', args=[obj.premium_card.pk])
            return format_html('<a href="{}">{}</a>', url, obj.premium_card.card_number)
        return 'N/A'
    card_identifier_display.short_description = 'Card'
    card_identifier_display.admin_order_field = 'vip_card__serial_number'
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def duration_display(self, obj):
        """Display activation duration"""
        duration = obj.duration
        if duration:
            total_seconds = duration.total_seconds()
            if total_seconds < 60:
                return f"{total_seconds:.1f}s"
            elif total_seconds < 3600:
                return f"{total_seconds/60:.1f}m"
            else:
                return f"{total_seconds/3600:.1f}h"
        return 'N/A'
    duration_display.short_description = 'Duration'
    
    def card_link(self, obj):
        """Link to the actual card"""
        if obj.vip_card:
            url = reverse('admin:accounts_vipdigitalcard_change', args=[obj.vip_card.pk])
            return format_html('<a href="{}">VIP Card: {}</a>', url, obj.vip_card.serial_number)
        elif obj.premium_card:
            url = reverse('admin:accounts_premiumdigitalcard_change', args=[obj.premium_card.pk])
            return format_html('<a href="{}">Premium Card: {}</a>', url, obj.premium_card.card_number)
        return 'No card linked'
    card_link.short_description = 'Linked Card'


@admin.register(CardUsageLog)  
class CardUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'card_display',
        'user_email',
        'event_type',
        'timestamp',
        'ip_address'
    ]
    
    list_filter = [
        'event_type',
        'timestamp',
    ]
    
    search_fields = [
        'user__email',
        'user__name',
        'vip_card__serial_number',
        'premium_card__card_number',
        'event_description'
    ]
    
    readonly_fields = ['id', 'timestamp']
    
    def card_display(self, obj):
        """Display card information"""
        if obj.vip_card:
            return f"VIP: {obj.vip_card.serial_number}"
        elif obj.premium_card:
            return f"Premium: {obj.premium_card.card_number}"
        return 'N/A'
    card_display.short_description = 'Card'
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'


# Inline admin for activation history
class CardActivationHistoryInline(admin.TabularInline):
    model = CardActivationHistory
    extra = 0
    readonly_fields = [
        'status',
        'attempted_at', 
        'completed_at',
        'activation_method',
        'ip_address',
        'user_agent',
        'error_message'
    ]
    
    fields = [
        'user',
        'status',
        'attempted_at',
        'completed_at', 
        'activation_method',
        'ip_address',
        'error_message'
    ]
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class CardUsageLogInline(admin.TabularInline):
    model = CardUsageLog
    extra = 0
    readonly_fields = ['timestamp', 'event_type', 'event_description', 'user']
    fields = ['timestamp', 'user', 'event_type', 'event_description']
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False