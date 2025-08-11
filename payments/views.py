# payments/views.py
"""
Payment system API views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Sum, Count, Q
import json
import logging
from decimal import Decimal
from datetime import timedelta, datetime

from .payment_models import (
    Payment, PaymentMethod, Currency, PaymentGateway,
    PaymentDispute, DriverPayout, PaymentAuditLog
)
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentMethodSerializer,
    CurrencySerializer, DriverPayoutSerializer, PaymentDisputeSerializer,
    PaymentSummarySerializer, RefundRequestSerializer
)
from .services import PaymentProcessor, CurrencyService, DriverPayoutService
from .gateways.paystack import PaystackGateway
from .gateways.flutterwave import FlutterwaveGateway
from .gateways.stripe_gateway import StripeGateway

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ModelViewSet):
    """Payment management ViewSet"""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get payments for current user"""
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all().select_related(
                'currency', 'gateway', 'payment_method'
            )
        
        # Regular users see their own payments
        return Payment.objects.filter(
            ride__user=user
        ).select_related('currency', 'gateway', 'payment_method')
    
    @action(detail=False, methods=['post'])
    def create_ride_payment(self, request):
        """Create payment for a ride"""
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                processor = PaymentProcessor()
                result = processor.create_ride_payment(
                    ride_id=serializer.validated_data['ride_id'],
                    payment_method_id=serializer.validated_data.get('payment_method_id'),
                    user=request.user,
                    metadata=serializer.validated_data.get('metadata', {})
                )
                
                if result['success']:
                    payment_serializer = PaymentSerializer(result['payment'])
                    return Response({
                        'success': True,
                        'payment': payment_serializer.data,
                        'gateway_response': result.get('gateway_response')
                    })
                else:
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"Payment creation failed: {str(e)}")
                return Response({
                    'success': False,
                    'error': 'Payment processing failed'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify payment status"""
        payment = self.get_object()
        
        try:
            processor = PaymentProcessor()
            result = processor.verify_payment(payment.id)
            
            # Refresh payment from database
            payment.refresh_from_db()
            serializer = PaymentSerializer(payment)
            
            return Response({
                'success': result['success'],
                'payment': serializer.data,
                'verification_data': result.get('data')
            })
            
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return Response({
                'success': False,
                'error': 'Verification failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process payment refund"""
        payment = self.get_object()
        serializer = RefundRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                processor = PaymentProcessor()
                result = processor.refund_payment(
                    payment_id=payment.id,
                    amount=serializer.validated_data.get('amount'),
                    reason=serializer.validated_data.get('reason', 'Customer requested refund')
                )
                
                if result['success']:
                    payment.refresh_from_db()
                    payment_serializer = PaymentSerializer(payment)
                    return Response({
                        'success': True,
                        'payment': payment_serializer.data,
                        'refund_data': result.get('refund_data')
                    })
                else:
                    return Response({
                        'success': False,
                        'error': result['error']
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"Refund processing failed: {str(e)}")
                return Response({
                    'success': False,
                    'error': 'Refund processing failed'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """Payment method management ViewSet"""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get payment methods for current user"""
        return PaymentMethod.objects.filter(
            user=self.request.user
        ).select_related('gateway')
    
    def perform_create(self, serializer):
        """Create payment method for current user"""
        serializer.save(user=self.request.user)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """Currency information ViewSet"""
    
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    queryset = Currency.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def exchange_rates(self, request):
        """Get current exchange rates"""
        try:
            currency_service = CurrencyService()
            rates = currency_service.get_all_exchange_rates()
            
            return Response({
                'success': True,
                'base_currency': 'USD',
                'rates': rates,
                'last_updated': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Exchange rates fetch failed: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to fetch exchange rates'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DriverPayoutViewSet(viewsets.ModelViewSet):
    """Driver payout management ViewSet"""
    
    serializer_class = DriverPayoutSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get payouts for current driver or all for staff"""
        user = self.request.user
        if user.is_staff:
            return DriverPayout.objects.all().select_related('currency', 'gateway')
        
        # Drivers see their own payouts
        return DriverPayout.objects.filter(
            driver=user
        ).select_related('currency', 'gateway')
    
    @action(detail=False, methods=['get'])
    def earnings_summary(self, request):
        """Get driver earnings summary"""
        if not hasattr(request.user, 'driver_profile'):
            return Response({
                'error': 'Driver profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            payout_service = DriverPayoutService()
            summary = payout_service.get_driver_earnings_summary(request.user.id)
            
            return Response({
                'success': True,
                'summary': summary
            })
            
        except Exception as e:
            logger.error(f"Earnings summary failed: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to get earnings summary'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Webhook handlers
@csrf_exempt
@require_POST
@api_view(['POST'])
@permission_classes([])
def paystack_webhook(request):
    """Handle Paystack webhook events"""
    try:
        payload = json.loads(request.body)
        signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
        
        # Initialize Paystack gateway for webhook verification
        gateway = PaystackGateway()
        
        if gateway.verify_webhook_signature(request.body, signature):
            # Process the webhook event
            event_type = payload.get('event')
            data = payload.get('data', {})
            
            logger.info(f"Paystack webhook received: {event_type}")
            
            if event_type == 'charge.success':
                # Handle successful payment
                reference = data.get('reference')
                if reference:
                    try:
                        payment = Payment.objects.get(gateway_reference=reference)
                        processor = PaymentProcessor()
                        processor.handle_successful_payment(payment.id, data)
                    except Payment.DoesNotExist:
                        logger.warning(f"Payment not found for reference: {reference}")
            
            elif event_type == 'transfer.success':
                # Handle successful payout
                transfer_reference = data.get('reference')
                if transfer_reference:
                    try:
                        payout = DriverPayout.objects.get(gateway_payout_id=transfer_reference)
                        payout_service = DriverPayoutService()
                        payout_service.handle_successful_payout(payout.id, data)
                    except DriverPayout.DoesNotExist:
                        logger.warning(f"Payout not found for reference: {transfer_reference}")
            
            return HttpResponse(status=200)
        else:
            logger.warning("Invalid Paystack webhook signature")
            return HttpResponse(status=400)
            
    except Exception as e:
        logger.error(f"Paystack webhook error: {str(e)}")
        return HttpResponse(status=500)


@csrf_exempt
@require_POST
@api_view(['POST'])
@permission_classes([])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    try:
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        
        # Initialize Stripe gateway for webhook verification
        gateway = StripeGateway()
        
        if gateway.verify_webhook_signature(payload, signature):
            event_data = json.loads(payload)
            event_type = event_data.get('type')
            data = event_data.get('data', {}).get('object', {})
            
            logger.info(f"Stripe webhook received: {event_type}")
            
            if event_type == 'payment_intent.succeeded':
                # Handle successful payment
                payment_intent_id = data.get('id')
                if payment_intent_id:
                    try:
                        payment = Payment.objects.get(gateway_transaction_id=payment_intent_id)
                        processor = PaymentProcessor()
                        processor.handle_successful_payment(payment.id, data)
                    except Payment.DoesNotExist:
                        logger.warning(f"Payment not found for intent: {payment_intent_id}")
            
            return HttpResponse(status=200)
        else:
            logger.warning("Invalid Stripe webhook signature")
            return HttpResponse(status=400)
            
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return HttpResponse(status=500)


class PaymentDisputeViewSet(viewsets.ModelViewSet):
    """Payment dispute management ViewSet"""
    
    serializer_class = PaymentDisputeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get disputes for current user"""
        user = self.request.user
        if user.is_staff:
            return PaymentDispute.objects.all().select_related('payment')
        
        # Regular users see their own disputes
        return PaymentDispute.objects.filter(
            payment__ride__user=user
        ).select_related('payment')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a payment dispute"""
        dispute = self.get_object()
        resolution = request.data.get('resolution')
        
        if not resolution:
            return Response(
                {'error': 'Resolution is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use transaction and check current state
            with transaction.atomic():
                # Refresh from database to get latest state
                dispute.refresh_from_db()
                
                # Check if dispute is still in a resolvable state
                if dispute.status == 'RESOLVED':
                    return Response(
                        {'error': 'Dispute has already been resolved'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if dispute.status not in ['PENDING', 'UNDER_REVIEW']:
                    return Response(
                        {'error': 'Dispute is not in a resolvable state'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                dispute.status = 'RESOLVED'
                dispute.resolution = resolution
                dispute.resolved_at = timezone.now()
                dispute.resolved_by = request.user
                dispute.save()
            
            return Response({
                'status': 'resolved',
                'dispute_id': str(dispute.id),
                'resolution': resolution
            })
            
        except Exception as e:
            logger.error(f"Error resolving dispute: {str(e)}")
            return Response(
                {'error': 'Failed to resolve dispute'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def commission_reports(request):
    """Get commission reports"""
    try:
        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            try:
                # Parse string dates into date objects
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Query payments in date range
        payments = Payment.objects.filter(
            created_at__date__range=[start_date, end_date],
            status='COMPLETED'
        )
        
        # Calculate commissions
        total_revenue = payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        platform_commission = payments.aggregate(
            total=Sum('platform_commission')
        )['total'] or Decimal('0.00')
        
        driver_commission = payments.aggregate(
            total=Sum('driver_commission')
        )['total'] or Decimal('0.00')
        
        hotel_commission = payments.aggregate(
            total=Sum('hotel_commission')
        )['total'] or Decimal('0.00')
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_payments': payments.count(),
                'total_revenue': total_revenue,
                'platform_commission': platform_commission,
                'driver_commission': driver_commission,
                'hotel_commission': hotel_commission
            },
            'breakdown': {
                'revenue_percentage': {
                    'platform': float(platform_commission / total_revenue * 100) if total_revenue > 0 else 0,
                    'drivers': float(driver_commission / total_revenue * 100) if total_revenue > 0 else 0,
                    'hotels': float(hotel_commission / total_revenue * 100) if total_revenue > 0 else 0
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating commission report: {str(e)}")
        return Response(
            {'error': 'Failed to generate commission report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """Get payment history for user"""
    try:
        user = request.user
        
        # Get user's payments
        payments = Payment.objects.filter(
            ride__user=user
        ).select_related(
            'currency', 'gateway', 'payment_method'
        ).order_by('-created_at')
        
        # Pagination
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_payments = payments[start:end]
        
        # Serialize payments
        serializer = PaymentSerializer(paginated_payments, many=True)
        
        return Response({
            'payments': serializer.data,
            'pagination': {
                'total': payments.count(),
                'page': page,
                'page_size': page_size,
                'has_next': end < payments.count(),
                'has_previous': page > 1
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting payment history: {str(e)}")
        return Response(
            {'error': 'Failed to get payment history'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gateway_status(request):
    """Get payment gateway status"""
    try:
        gateways = PaymentGateway.objects.filter(is_active=True)
        
        gateway_status = []
        for gateway in gateways:
            # Check gateway health
            try:
                if gateway.name.lower() == 'paystack':
                    paystack = PaystackGateway()
                    health = paystack.health_check()
                elif gateway.name.lower() == 'flutterwave':
                    flutterwave = FlutterwaveGateway()
                    health = flutterwave.health_check()
                elif gateway.name.lower() == 'stripe':
                    stripe = StripeGateway()
                    health = stripe.health_check()
                else:
                    health = {'status': 'unknown'}
                
                gateway_status.append({
                    'name': gateway.name,
                    'is_active': gateway.is_active,
                    'health': health.get('status', 'unknown'),
                    'last_checked': timezone.now().isoformat()
                })
                
            except Exception as e:
                gateway_status.append({
                    'name': gateway.name,
                    'is_active': False,
                    'health': 'error',
                    'error': str(e),
                    'last_checked': timezone.now().isoformat()
                })
        
        return Response({
            'gateways': gateway_status,
            'overall_health': 'healthy' if all(
                g['health'] == 'healthy' for g in gateway_status
            ) else 'degraded'
        })
        
    except Exception as e:
        logger.error(f"Error checking gateway status: {str(e)}")
        return Response(
            {'error': 'Failed to check gateway status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@csrf_exempt
def flutterwave_webhook(request):
    """Handle Flutterwave webhook events - placeholder"""
    return Response({'message': 'Flutterwave webhook handler'})
