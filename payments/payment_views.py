# payments/payment_views.py
"""
Payment processing API views with multi-gateway support
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from decimal import Decimal
from datetime import timedelta
import logging
import json

from .payment_models import Payment, PaymentMethod, Currency, PaymentDispute, DriverPayout
from .services import PaymentProcessor, CurrencyService, DriverPayoutService, DisputeService
from .serializers import (
    PaymentSerializer, PaymentMethodSerializer, CurrencySerializer,
    PaymentDisputeSerializer, DriverPayoutSerializer  #, PaymentCreateSerializer
)
# from rides.models import Ride  # Temporarily commented out
# from accounts.permissions import TierBasedPermission, VIPOnlyPermission  # Temporarily commented out

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ModelViewSet):
    """Payment management API"""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()  # Default queryset, will be filtered in get_queryset
    
    def get_queryset(self):
        """Filter payments by user"""
        user = self.request.user
        if hasattr(user, 'driver') and user.driver:
            # Drivers can see their payout-related payments
            return Payment.objects.filter(
                user=user
            ).select_related('currency', 'gateway', 'ride')
        else:
            # Regular users see their own payments
            return Payment.objects.filter(
                user=user
            ).select_related('currency', 'gateway', 'ride')
    
    # @action(detail=False, methods=['post'])
    # def create_ride_payment(self, request):
    #     """Create payment for a ride"""
    #     # Temporarily commented out due to Ride dependency
    #     pass
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify payment with gateway"""
        payment = self.get_object()
        
        if payment.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        processor = PaymentProcessor()
        
        try:
            success = processor.verify_payment(payment)
            payment.refresh_from_db()
            
            return Response({
                'success': success,
                'status': payment.status,
                'message': 'Payment verified successfully' if success else 'Payment verification failed'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process payment refund"""
        payment = self.get_object()
        
        # Only VIP users or staff can request refunds
        if not (request.user.tier == 'vip' or request.user.is_staff):
            return Response(
                {'error': 'Refund not available for your tier'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        amount = request.data.get('amount')
        reason = request.data.get('reason', 'Customer requested refund')
        
        if amount:
            try:
                amount = Decimal(str(amount))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid amount'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            processor = PaymentProcessor()
            refund_payment = processor.process_refund(payment, amount, reason)
            
            return Response(
                PaymentSerializer(refund_payment).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """Payment method management API"""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    queryset = PaymentMethod.objects.all()
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('gateway')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default"""
        payment_method = self.get_object()
        
        # Remove default from other methods
        PaymentMethod.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Set this as default
        payment_method.is_default = True
        payment_method.save()
        
        return Response({'message': 'Payment method set as default'})


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """Currency information API"""
    
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    queryset = Currency.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def exchange_rates(self, request):
        """Get current exchange rates"""
        base_currency = request.query_params.get('base', 'USD')
        target_currencies = request.query_params.getlist('targets[]')
        
        if not target_currencies:
            target_currencies = ['NGN', 'EUR', 'GBP', 'CAD']
        
        currency_service = CurrencyService()
        rates = {}
        
        for target in target_currencies:
            try:
                rate = currency_service.get_exchange_rate(base_currency, target)
                rates[target] = float(rate)
            except Exception as e:
                rates[target] = None
        
        return Response({
            'base': base_currency,
            'rates': rates,
            'timestamp': timezone.now().isoformat()
        })


class DriverPayoutViewSet(viewsets.ReadOnlyModelViewSet):
    """Driver payout information API"""
    
    serializer_class = DriverPayoutSerializer
    permission_classes = [IsAuthenticated]
    queryset = DriverPayout.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if not (hasattr(user, 'driver') and user.driver):
            return DriverPayout.objects.none()
        
        return DriverPayout.objects.filter(
            driver=user.driver
        ).select_related('currency', 'gateway')
    
    @action(detail=False, methods=['get'])
    def earnings_summary(self, request):
        """Get driver earnings summary"""
        user = request.user
        
        if not (hasattr(user, 'driver') and user.driver):
            return Response(
                {'error': 'Driver profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get period from query params
        period = request.query_params.get('period', 'current_month')
        
        if period == 'current_month':
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now()
        elif period == 'last_month':
            current_month = timezone.now().replace(day=1)
            end_date = current_month - timedelta(days=1)
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to current month
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now()
        
        payout_service = DriverPayoutService()
        earnings_data = payout_service.calculate_driver_earnings(
            user.driver, start_date, end_date
        )
        
        return Response(earnings_data)


class PaymentDisputeViewSet(viewsets.ModelViewSet):
    """Payment dispute management ViewSet"""
    
    serializer_class = PaymentDisputeSerializer
    permission_classes = [IsAuthenticated]
    queryset = PaymentDispute.objects.all()
    
    def get_queryset(self):
        """Get disputes for current user or all for staff"""
        user = self.request.user
        if user.is_staff:
            return PaymentDispute.objects.all().select_related(
                'payment', 'currency'
            )
        
        # Regular users see disputes for their payments
        return PaymentDispute.objects.filter(
            payment__ride__user=user
        ).select_related('payment', 'currency')


# Webhook views for payment gateways


@csrf_exempt
@require_http_methods(["POST"])
def paystack_webhook(request):
    """Handle Paystack webhooks"""
    try:
        payload = request.body.decode('utf-8')
        signature = request.headers.get('X-Paystack-Signature', '')
        
        # Verify signature
        processor = PaymentProcessor()
        gateway = processor.get_gateway('paystack')
        
        if not gateway.verify_webhook_signature(payload, signature):
            return HttpResponse(status=400)
        
        data = json.loads(payload)
        event_type = data.get('event')
        
        if event_type == 'charge.success':
            # Handle successful payment
            reference = data['data']['reference']
            
            payment = Payment.objects.filter(
                gateway_reference=reference
            ).first()
            
            if payment and payment.status == Payment.PaymentStatus.PROCESSING:
                processor.verify_payment(payment)
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Paystack webhook error: {e}")
        return HttpResponse(status=500)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    try:
        payload = request.body.decode('utf-8')
        signature = request.headers.get('Stripe-Signature', '')
        
        # Verify signature
        processor = PaymentProcessor()
        gateway = processor.get_gateway('stripe')
        
        if not gateway.verify_webhook_signature(payload, signature):
            return HttpResponse(status=400)
        
        data = json.loads(payload)
        event_type = data.get('type')
        
        if event_type == 'payment_intent.succeeded':
            # Handle successful payment
            payment_intent_id = data['data']['object']['id']
            
            payment = Payment.objects.filter(
                gateway_transaction_id=payment_intent_id
            ).first()
            
            if payment and payment.status == Payment.PaymentStatus.PROCESSING:
                processor.verify_payment(payment)
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return HttpResponse(status=500)


@csrf_exempt
@require_http_methods(["POST"])
def flutterwave_webhook(request):
    """Handle Flutterwave webhooks"""
    try:
        payload = request.body.decode('utf-8')
        signature = request.headers.get('verif-hash', '')
        
        # Verify signature
        processor = PaymentProcessor()
        gateway = processor.get_gateway('flutterwave')
        
        if not gateway.verify_webhook_signature(payload, signature):
            return HttpResponse(status=400)
        
        data = json.loads(payload)
        event_type = data.get('event')
        
        if event_type == 'charge.completed':
            # Handle successful payment
            tx_ref = data['data']['tx_ref']
            
            payment = Payment.objects.filter(
                gateway_reference=tx_ref
            ).first()
            
            if payment and payment.status == Payment.PaymentStatus.PROCESSING:
                processor.verify_payment(payment)
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Flutterwave webhook error: {e}")
        return HttpResponse(status=500)
