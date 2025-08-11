"""
Admin interface for payment system
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from django.forms import TextInput, Textarea
from .payment_models import (
    Currency, PaymentGateway, PaymentMethod, Payment,
    PaymentDispute, DriverPayout, ExchangeRate, PaymentAuditLog
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'symbol', 'usd_exchange_rate',
        'last_rate_update', 'is_active'
    ]
    list_filter = ['is_active', 'last_rate_update']
    search_fields = ['code', 'name']
    readonly_fields = ['last_rate_update']
    ordering = ['code']


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'gateway_type', 'is_active', 'priority_order',
        'supports_payouts', 'supports_disputes'
    ]
    list_filter = [
        'gateway_type', 'is_active', 'supports_payouts',
        'supports_disputes', 'supports_subscriptions'
    ]
    search_fields = ['name', 'gateway_type']
    filter_horizontal = ['supported_currencies']
    ordering = ['priority_order', 'name']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'method_type', 'gateway', 'masked_token',
        'is_active', 'is_default', 'is_verified', 'created_at'
    ]
    list_filter = [
        'method_type', 'gateway', 'is_active',
        'is_default', 'is_verified', 'created_at'
    ]
    search_fields = ['user__email', 'user__phone', 'last_four_digits']
    readonly_fields = ['gateway_token', 'created_at']
    ordering = ['-created_at']
    
    def masked_token(self, obj):
        """Display masked gateway token (PCI DSS compliant)"""
        if obj.gateway_token:
            token_len = len(obj.gateway_token)
            return f"***{obj.gateway_token[-4:]}" if token_len > 4 else "***"
        return "-"
    masked_token.short_description = "Token"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'ride_info', 'user_info', 'status', 'amount_display',
        'gateway', 'user_tier', 'commission_amount', 'created_at'
    ]
    list_filter = [
        'status', 'payment_type', 'gateway', 'user_tier',
        'currency', 'initiated_at', 'processed_at'
    ]
    search_fields = [
        'id', 'ride__id', 'gateway_transaction_id',
        'gateway_reference', 'ride__user__email'
    ]
    readonly_fields = [
        'id', 'gateway_transaction_id', 'gateway_reference',
        'gateway_fee', 'platform_fee', 'net_amount',
        'commission_amount', 'driver_payout_amount',
        'initiated_at', 'processed_at', 'failed_at'
    ]
    date_hierarchy = 'initiated_at'
    ordering = ['-initiated_at']
    
    def ride_info(self, obj):
        """Display ride information"""
        if obj.ride:
            return format_html(
                '<a href="/admin/rides/ride/{}/change/">{}</a>',
                obj.ride.id, str(obj.ride.id)[:8]
            )
        return "-"
    ride_info.short_description = "Ride"
    
    def user_info(self, obj):
        """Display user information"""
        if obj.ride and obj.ride.user:
            user = obj.ride.user
            return format_html(
                '<a href="/admin/accounts/user/{}/change/">{}</a>',
                user.id, user.email or user.phone
            )
        return "-"
    user_info.short_description = "User"
    
    def amount_display(self, obj):
        """Display formatted amount"""
        return f"{obj.amount} {obj.currency.code}"
    amount_display.short_description = "Amount"


@admin.register(PaymentDispute)
class PaymentDisputeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'payment_link', 'dispute_reason', 'status',
        'disputed_amount_display', 'dispute_date', 'resolved_date'
    ]
    list_filter = [
        'status', 'dispute_reason', 'dispute_date',
        'resolved_date', 'resolution_outcome'
    ]
    search_fields = [
        'id', 'payment__id', 'gateway_dispute_id',
        'customer_message', 'merchant_response'
    ]
    readonly_fields = [
        'gateway_dispute_id', 'dispute_date', 'evidence_due_date',
        'resolved_date', 'resolution_outcome', 'resolution_amount',
        'created_at'
    ]
    date_hierarchy = 'dispute_date'
    ordering = ['-dispute_date']
    
    def payment_link(self, obj):
        """Display payment link"""
        return format_html(
            '<a href="/admin/payments/payment/{}/change/">{}</a>',
            obj.payment.id, str(obj.payment.id)[:8]
        )
    payment_link.short_description = "Payment"
    
    def disputed_amount_display(self, obj):
        """Display formatted disputed amount"""
        return f"{obj.disputed_amount} {obj.currency.code}"
    disputed_amount_display.short_description = "Disputed Amount"


@admin.register(DriverPayout)
class DriverPayoutAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'driver_link', 'status', 'net_payout_display',
        'period_display', 'scheduled_date', 'processed_date'
    ]
    list_filter = [
        'status', 'payout_method', 'currency',
        'scheduled_date', 'processed_date', 'completed_date'
    ]
    search_fields = [
        'id', 'driver__email', 'driver__phone',
        'gateway_payout_id'
    ]
    readonly_fields = [
        'gross_earnings', 'commission_deducted',
        'gateway_fees_deducted', 'tax_deducted',
        'other_deductions', 'net_payout_amount',
        'processed_date', 'completed_date',
        'failure_reason', 'retry_count', 'created_at'
    ]
    date_hierarchy = 'scheduled_date'
    ordering = ['-scheduled_date']
    
    def driver_link(self, obj):
        """Display driver link"""
        return format_html(
            '<a href="/admin/accounts/driver/{}/change/">{}</a>',
            obj.driver.id, obj.driver.email or obj.driver.phone
        )
    driver_link.short_description = "Driver"
    
    def net_payout_display(self, obj):
        """Display formatted net payout amount"""
        return f"{obj.net_payout_amount} {obj.currency.code}"
    net_payout_display.short_description = "Net Payout"
    
    def period_display(self, obj):
        """Display payout period"""
        return f"{obj.period_start.date()} to {obj.period_end.date()}"
    period_display.short_description = "Period"


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = [
        'currency_pair', 'rate', 'rate_source',
        'effective_date', 'created_at'
    ]
    list_filter = [
        'base_currency', 'target_currency', 'rate_source',
        'effective_date', 'created_at'
    ]
    search_fields = [
        'base_currency__code', 'target_currency__code', 'rate_source'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'effective_date'
    ordering = ['-effective_date']
    
    def currency_pair(self, obj):
        """Display currency pair"""
        return f"{obj.base_currency.code}/{obj.target_currency.code}"
    currency_pair.short_description = "Currency Pair"


@admin.register(PaymentAuditLog)
class PaymentAuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'action_type', 'user_display', 'description_short',
        'timestamp'
    ]
    list_filter = [
        'action_type', 'timestamp'
    ]
    search_fields = [
        'action_type', 'description', 'user__email',
        'user_ip'
    ]
    readonly_fields = [
        'id', 'action_type', 'description', 'user',
        'user_ip', 'payment', 'dispute', 'payout',
        'old_values', 'new_values', 'metadata', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def user_display(self, obj):
        """Display user information"""
        if obj.user:
            return obj.user.email or obj.user.phone
        return "System"
    user_display.short_description = "User"
    
    def description_short(self, obj):
        """Display shortened description"""
        desc_len = len(obj.description)
        return obj.description[:50] + "..." if desc_len > 50 else obj.description
    description_short.short_description = "Description"
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent modification of audit logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs"""
        return False
