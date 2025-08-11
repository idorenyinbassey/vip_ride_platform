# payments/serializers.py
"""
Payment system serializers for API responses
"""

from rest_framework import serializers
from decimal import Decimal
from .payment_models import (
    Payment, PaymentMethod, Currency, PaymentGateway,
    PaymentDispute, DriverPayout, ExchangeRate, PaymentAuditLog
)


class CurrencySerializer(serializers.ModelSerializer):
    """Currency serializer"""
    
    class Meta:
        model = Currency
        fields = [
            'code', 'name', 'symbol', 'decimal_places',
            'usd_exchange_rate', 'last_rate_update', 'is_active'
        ]
        read_only_fields = ['last_rate_update']


class PaymentGatewaySerializer(serializers.ModelSerializer):
    """Payment gateway serializer (without sensitive config)"""
    
    supported_currencies = CurrencySerializer(many=True, read_only=True)
    
    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'name', 'gateway_type', 'supported_currencies',
            'supports_payouts', 'supports_disputes', 'supports_subscriptions',
            'is_active', 'priority_order', 'supported_countries'
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Payment method serializer"""
    
    gateway = PaymentGatewaySerializer(read_only=True)
    gateway_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'method_type', 'gateway', 'gateway_id', 'gateway_token',
            'last_four_digits', 'brand', 'expiry_month', 'expiry_year',
            'is_active', 'is_default', 'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']
        extra_kwargs = {
            'gateway_token': {'write_only': True}
        }


class PaymentSerializer(serializers.ModelSerializer):
    """Payment transaction serializer"""
    
    currency = CurrencySerializer(read_only=True)
    gateway = PaymentGatewaySerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    
    # Calculated fields
    total_fees = serializers.SerializerMethodField()
    net_rider_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'ride', 'payment_type', 'status', 'amount', 'currency',
            'usd_amount', 'gateway', 'payment_method', 'gateway_transaction_id',
            'gateway_reference', 'gateway_fee', 'platform_fee', 'net_amount',
            'user_tier', 'commission_rate', 'commission_amount',
            'driver_payout_amount', 'total_fees', 'net_rider_amount',
            'initiated_at', 'processed_at', 'failed_at', 'failure_reason',
            'retry_count', 'metadata'
        ]
        read_only_fields = [
            'id', 'gateway_transaction_id', 'gateway_reference',
            'gateway_fee', 'platform_fee', 'net_amount', 'commission_amount',
            'driver_payout_amount', 'initiated_at', 'processed_at',
            'failed_at', 'total_fees', 'net_rider_amount'
        ]
    
    def get_total_fees(self, obj):
        """Calculate total fees"""
        return obj.gateway_fee + obj.platform_fee
    
    def get_net_rider_amount(self, obj):
        """Calculate net amount paid by rider"""
        return obj.amount + obj.gateway_fee + obj.platform_fee


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payments"""
    
    ride_id = serializers.UUIDField()
    payment_method_id = serializers.UUIDField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_ride_id(self, value):
        """Validate ride exists and belongs to user"""
        from rides.models import Ride
        
        try:
            ride = Ride.objects.get(id=value)
        except Ride.DoesNotExist:
            raise serializers.ValidationError("Ride not found")
        
        # Additional validation would be done in the view
        return value


class PaymentDisputeSerializer(serializers.ModelSerializer):
    """Payment dispute serializer"""
    
    payment = PaymentSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = PaymentDispute
        fields = [
            'id', 'payment', 'dispute_reason', 'status', 'disputed_amount',
            'currency', 'gateway_dispute_id', 'dispute_date',
            'evidence_due_date', 'resolved_date', 'customer_message',
            'merchant_response', 'evidence_files', 'resolution_outcome',
            'resolution_amount', 'created_at'
        ]
        read_only_fields = [
            'id', 'gateway_dispute_id', 'dispute_date', 'evidence_due_date',
            'resolved_date', 'merchant_response', 'resolution_outcome',
            'resolution_amount', 'created_at'
        ]


class DriverPayoutSerializer(serializers.ModelSerializer):
    """Driver payout serializer"""
    
    currency = CurrencySerializer(read_only=True)
    gateway = PaymentGatewaySerializer(read_only=True)
    
    # Summary fields
    total_deductions = serializers.SerializerMethodField()
    payout_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = DriverPayout
        fields = [
            'id', 'status', 'payout_method', 'gross_earnings',
            'commission_deducted', 'gateway_fees_deducted', 'tax_deducted',
            'other_deductions', 'total_deductions', 'net_payout_amount',
            'payout_percentage', 'currency', 'period_start', 'period_end',
            'gateway', 'scheduled_date', 'processed_date', 'completed_date',
            'failure_reason', 'retry_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'gross_earnings', 'commission_deducted',
            'gateway_fees_deducted', 'tax_deducted', 'other_deductions',
            'net_payout_amount', 'total_deductions', 'payout_percentage',
            'processed_date', 'completed_date', 'failure_reason',
            'retry_count', 'created_at'
        ]
    
    def get_total_deductions(self, obj):
        """Calculate total deductions"""
        return (obj.commission_deducted + obj.gateway_fees_deducted +
                obj.tax_deducted + obj.other_deductions)
    
    def get_payout_percentage(self, obj):
        """Calculate payout percentage of gross earnings"""
        if obj.gross_earnings > 0:
            return float((obj.net_payout_amount / obj.gross_earnings) * 100)
        return 0.0


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Exchange rate serializer"""
    
    base_currency = CurrencySerializer(read_only=True)
    target_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = ExchangeRate
        fields = [
            'base_currency', 'target_currency', 'rate', 'rate_source',
            'effective_date', 'created_at'
        ]


class PaymentAuditLogSerializer(serializers.ModelSerializer):
    """Payment audit log serializer"""
    
    payment = PaymentSerializer(read_only=True)
    dispute = PaymentDisputeSerializer(read_only=True)
    payout = DriverPayoutSerializer(read_only=True)
    
    class Meta:
        model = PaymentAuditLog
        fields = [
            'id', 'action_type', 'description', 'user', 'user_ip',
            'payment', 'dispute', 'payout', 'old_values', 'new_values',
            'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class PaymentSummarySerializer(serializers.Serializer):
    """Payment summary for dashboards"""
    
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_refunded = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_payments = serializers.IntegerField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    driver_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    period = serializers.CharField(max_length=50)


class CommissionBreakdownSerializer(serializers.Serializer):
    """Commission breakdown by user tier"""
    
    user_tier = serializers.CharField(max_length=10)
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_rides = serializers.IntegerField()
    total_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_commission_per_ride = serializers.DecimalField(max_digits=10, decimal_places=2)


class GatewayPerformanceSerializer(serializers.Serializer):
    """Gateway performance metrics"""
    
    gateway_name = serializers.CharField(max_length=50)
    gateway_type = serializers.CharField(max_length=20)
    total_transactions = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_volume = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_transaction_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fees_collected = serializers.DecimalField(max_digits=12, decimal_places=2)


class CurrencyConversionSerializer(serializers.Serializer):
    """Currency conversion request/response"""
    
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    converted_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    exchange_rate = serializers.DecimalField(max_digits=12, decimal_places=6, read_only=True)
    conversion_timestamp = serializers.DateTimeField(read_only=True)


class PaymentMethodTokenizeSerializer(serializers.Serializer):
    """Payment method tokenization request"""
    
    gateway_type = serializers.ChoiceField(
        choices=['paystack', 'flutterwave', 'stripe']
    )
    payment_data = serializers.JSONField()
    method_type = serializers.ChoiceField(
        choices=PaymentMethod.MethodType.choices
    )
    
    def validate_payment_data(self, value):
        """Validate payment data based on gateway type"""
        gateway_type = self.initial_data.get('gateway_type')
        
        if gateway_type == 'stripe':
            required_fields = ['type']
            if value.get('type') == 'card':
                required_fields.extend(['card[number]', 'card[exp_month]', 'card[exp_year]', 'card[cvc]'])
        elif gateway_type == 'paystack':
            required_fields = ['email']
        elif gateway_type == 'flutterwave':
            required_fields = ['email']
        else:
            raise serializers.ValidationError("Unsupported gateway type")
        
        missing_fields = [field for field in required_fields if field not in value]
        if missing_fields:
            raise serializers.ValidationError(f"Missing required fields: {missing_fields}")
        
        return value


class RefundRequestSerializer(serializers.Serializer):
    """Refund request serializer"""
    
    payment_id = serializers.UUIDField()
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=False, 
        allow_null=True
    )
    reason = serializers.CharField(max_length=500, required=False, default='Customer requested refund')
    
    def validate_payment_id(self, value):
        """Validate payment exists and is refundable"""
        try:
            payment = Payment.objects.get(id=value)
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found")
        
        if payment.status != Payment.PaymentStatus.SUCCEEDED:
            raise serializers.ValidationError("Only successful payments can be refunded")
        
        return value
    
    def validate_amount(self, value):
        """Validate refund amount"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Refund amount must be positive")
        
        return value


class WebhookEventSerializer(serializers.Serializer):
    """Webhook event data serializer"""
    
    gateway_type = serializers.CharField(max_length=20)
    event_type = serializers.CharField(max_length=50)
    event_data = serializers.JSONField()
    signature = serializers.CharField(max_length=200)
    processed = serializers.BooleanField(default=False)
    processing_error = serializers.CharField(max_length=500, required=False, allow_blank=True)
