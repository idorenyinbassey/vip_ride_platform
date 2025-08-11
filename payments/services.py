# payments/services.py
"""
Payment processing services with multi-gateway support and PCI DSS compliance
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.db import transaction, models
from django.utils import timezone
from django.core.cache import cache
import logging

from .payment_models import (
    Payment, PaymentGateway, Currency, PaymentMethod, 
    PaymentDispute, DriverPayout, ExchangeRate, PaymentAuditLog
)
from .gateways.paystack import PaystackGateway
from .gateways.flutterwave import FlutterwaveGateway
from .gateways.stripe_gateway import StripeGateway
from .gateways.base import BasePaymentGateway, PaymentGatewayResponse
from accounts.models import UserTier
from rides.models import Ride

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """Central payment processing service"""
    
    def __init__(self):
        self.gateway_classes = {
            'paystack': PaystackGateway,
            'flutterwave': FlutterwaveGateway,
            'stripe': StripeGateway,
        }
    
    def get_gateway(self, gateway_type: str, config: Dict = None) -> BasePaymentGateway:
        """Get gateway instance"""
        if gateway_type not in self.gateway_classes:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")
        
        if config is None:
            # Get config from database
            gateway_obj = PaymentGateway.objects.filter(
                gateway_type=gateway_type,
                is_active=True
            ).first()
            
            if not gateway_obj:
                raise ValueError(f"No active gateway found for {gateway_type}")
            
            config = gateway_obj.decrypt_config()
        
        return self.gateway_classes[gateway_type](config)
    
    def select_best_gateway(self, currency: str, amount: Decimal, 
                           user_tier: str = None) -> PaymentGateway:
        """Select best gateway based on currency, amount, and user tier"""
        
        # Get active gateways that support the currency
        gateways = PaymentGateway.objects.filter(
            is_active=True,
            supported_currencies__code=currency
        ).order_by('priority_order')
        
        # VIP users get priority gateways
        if user_tier == UserTier.VIP:
            vip_gateways = gateways.filter(gateway_type='stripe')
            if vip_gateways.exists():
                return vip_gateways.first()
        
        # For large amounts, prefer more reliable gateways
        if amount > Decimal('1000'):
            reliable_gateways = gateways.filter(
                gateway_type__in=['stripe', 'paystack']
            )
            if reliable_gateways.exists():
                return reliable_gateways.first()
        
        # Return first available gateway
        return gateways.first()
    
    def process_ride_payment(self, ride: Ride, payment_method: PaymentMethod = None,
                            metadata: Dict = None) -> Payment:
        """Process payment for a ride"""
        
        with transaction.atomic():
            # Calculate final fare
            ride.calculate_final_fare()
            
            # Get user's default currency or ride currency
            currency = Currency.objects.filter(is_default=True).first()
            if not currency:
                currency = Currency.objects.get(code='USD')
            
            # Select best gateway
            gateway_obj = self.select_best_gateway(
                currency.code, 
                ride.total_fare, 
                ride.rider_tier
            )
            
            # Create payment record
            payment = Payment.objects.create(
                ride=ride,
                user=ride.rider,
                payment_type=Payment.PaymentType.RIDE_PAYMENT,
                amount=ride.total_fare,
                currency=currency,
                usd_amount=currency.convert_to_usd(ride.total_fare),
                gateway=gateway_obj,
                payment_method=payment_method,
                user_tier=ride.rider_tier,
                commission_rate=self._get_commission_rate(ride.rider_tier),
                metadata=metadata or {}
            )
            
            # Calculate commission
            payment.calculate_commission()
            payment.save()
            
            # Process payment through gateway
            gateway = self.get_gateway(gateway_obj.gateway_type)
            
            payment_metadata = {
                'email': ride.rider.email,
                'name': ride.rider.get_full_name(),
                'ride_id': str(ride.id),
                'payment_id': str(payment.id)
            }
            
            if metadata:
                payment_metadata.update(metadata)
            
            response = gateway.create_payment_intent(
                payment.amount,
                currency.code,
                payment_metadata
            )
            
            if response.success:
                payment.gateway_transaction_id = response.transaction_id
                payment.gateway_reference = response.reference
                payment.gateway_response = response.raw_response
                payment.status = Payment.PaymentStatus.PROCESSING
                payment.save()
                
                # Log audit
                self._log_payment_audit(
                    PaymentAuditLog.ActionType.PAYMENT_CREATED,
                    f"Payment created for ride {ride.id}",
                    payment=payment,
                    user=ride.rider
                )
                
                return payment
            else:
                payment.status = Payment.PaymentStatus.FAILED
                payment.failure_reason = response.message
                payment.save()
                
                self._log_payment_audit(
                    PaymentAuditLog.ActionType.PAYMENT_FAILED,
                    f"Payment creation failed: {response.message}",
                    payment=payment,
                    user=ride.rider
                )
                
                raise Exception(f"Payment processing failed: {response.message}")
    
    def verify_payment(self, payment: Payment) -> bool:
        """Verify payment status with gateway"""
        
        gateway = self.get_gateway(payment.gateway.gateway_type)
        response = gateway.get_payment_status(payment.gateway_transaction_id)
        
        if response.success:
            payment.status = Payment.PaymentStatus.SUCCEEDED
            payment.processed_at = timezone.now()
            payment.gateway_fee = response.fee or Decimal('0')
            payment.net_amount = payment.amount - payment.gateway_fee
            payment.save()
            
            # Update ride status if this was a ride payment
            if payment.ride:
                from rides.workflow import RideWorkflow
                workflow = RideWorkflow(payment.ride)
                workflow.transition_to('payment_completed')
            
            self._log_payment_audit(
                PaymentAuditLog.ActionType.PAYMENT_PROCESSED,
                f"Payment verified successfully",
                payment=payment
            )
            
            return True
        else:
            payment.status = Payment.PaymentStatus.FAILED
            payment.failed_at = timezone.now()
            payment.failure_reason = response.message
            payment.save()
            
            self._log_payment_audit(
                PaymentAuditLog.ActionType.PAYMENT_FAILED,
                f"Payment verification failed: {response.message}",
                payment=payment
            )
            
            return False
    
    def process_refund(self, payment: Payment, amount: Decimal = None, 
                      reason: str = None) -> Payment:
        """Process a refund"""
        
        if payment.status != Payment.PaymentStatus.SUCCEEDED:
            raise ValueError("Can only refund successful payments")
        
        refund_amount = amount or payment.amount
        
        with transaction.atomic():
            # Create refund payment record
            refund_payment = Payment.objects.create(
                ride=payment.ride,
                user=payment.user,
                payment_type=Payment.PaymentType.REFUND,
                amount=refund_amount,
                currency=payment.currency,
                usd_amount=payment.currency.convert_to_usd(refund_amount),
                gateway=payment.gateway,
                user_tier=payment.user_tier,
                commission_rate=Decimal('0'),
                metadata={'original_payment_id': str(payment.id)}
            )
            
            # Process refund through gateway
            gateway = self.get_gateway(payment.gateway.gateway_type)
            response = gateway.refund_payment(
                payment.gateway_transaction_id,
                refund_amount,
                reason
            )
            
            if response.success:
                refund_payment.gateway_transaction_id = response.transaction_id
                refund_payment.gateway_reference = response.reference
                refund_payment.status = Payment.PaymentStatus.SUCCEEDED
                refund_payment.processed_at = timezone.now()
                refund_payment.save()
                
                # Update original payment status
                if refund_amount >= payment.amount:
                    payment.status = Payment.PaymentStatus.REFUNDED
                else:
                    payment.status = Payment.PaymentStatus.PARTIALLY_REFUNDED
                payment.save()
                
                self._log_payment_audit(
                    PaymentAuditLog.ActionType.REFUND_ISSUED,
                    f"Refund processed: {refund_amount} {payment.currency.code}",
                    payment=refund_payment,
                    user=payment.user
                )
                
                return refund_payment
            else:
                refund_payment.status = Payment.PaymentStatus.FAILED
                refund_payment.failure_reason = response.message
                refund_payment.save()
                
                raise Exception(f"Refund processing failed: {response.message}")
    
    def _get_commission_rate(self, user_tier: str) -> Decimal:
        """Get commission rate based on user tier"""
        rates = {
            UserTier.NORMAL: Decimal('15.0'),    # 15%
            UserTier.PREMIUM: Decimal('22.5'),   # 22.5%
            UserTier.VIP: Decimal('27.5'),       # 27.5%
        }
        return rates.get(user_tier, rates[UserTier.NORMAL])
    
    def _log_payment_audit(self, action_type: str, description: str, 
                          payment: Payment = None, user = None, 
                          old_values: Dict = None, new_values: Dict = None):
        """Log payment audit entry"""
        PaymentAuditLog.objects.create(
            action_type=action_type,
            description=description,
            user=user,
            payment=payment,
            old_values=old_values or {},
            new_values=new_values or {}
        )


class CurrencyService:
    """Currency and exchange rate management"""
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Get current exchange rate between currencies"""
        cache_key = f"exchange_rate_{from_currency}_{to_currency}"
        rate = cache.get(cache_key)
        
        if rate is None:
            try:
                from_curr = Currency.objects.get(code=from_currency, is_active=True)
                to_curr = Currency.objects.get(code=to_currency, is_active=True)
                
                if from_currency == to_currency:
                    rate = Decimal('1.0')
                else:
                    # Convert through USD
                    usd_amount = from_curr.convert_to_usd(Decimal('1'))
                    rate = to_curr.convert_from_usd(usd_amount)
                
                # Cache for 5 minutes
                cache.set(cache_key, rate, 300)
                
            except Currency.DoesNotExist:
                raise ValueError(f"Currency not found: {from_currency} or {to_currency}")
        
        return rate
    
    def convert_amount(self, amount: Decimal, from_currency: str, 
                      to_currency: str) -> Decimal:
        """Convert amount between currencies"""
        if from_currency == to_currency:
            return amount
        
        rate = self.get_exchange_rate(from_currency, to_currency)
        return amount * rate
    
    def update_exchange_rates(self):
        """Update exchange rates from external API"""
        # This would integrate with a real exchange rate API
        # For now, this is a placeholder
        logger.info("Exchange rates update requested")
        pass


class DriverPayoutService:
    """Driver payout management"""
    
    def __init__(self):
        self.payment_processor = PaymentProcessor()
    
    def calculate_driver_earnings(self, driver, period_start, period_end) -> Dict:
        """Calculate driver earnings for a period"""
        
        # Get all completed rides in the period
        rides = Ride.objects.filter(
            driver=driver,
            status='completed',
            completed_at__gte=period_start,
            completed_at__lte=period_end
        )
        
        total_rides = rides.count()
        gross_earnings = sum((ride.total_fare for ride in rides), Decimal('0'))
        
        # Calculate deductions
        commission_total = Decimal('0')
        for ride in rides:
            if ride.rider_tier == UserTier.VIP:
                commission_rate = Decimal('0.275')
            elif ride.rider_tier == UserTier.PREMIUM:
                commission_rate = Decimal('0.225')
            else:
                commission_rate = Decimal('0.15')
            
            commission_total += ride.total_fare * commission_rate
        
        # Get gateway fees from payments
        gateway_fees = Payment.objects.filter(
            ride__in=rides,
            status=Payment.PaymentStatus.SUCCEEDED
        ).aggregate(total_fees=models.Sum('gateway_fee'))['total_fees'] or Decimal('0')
        
        net_earnings = gross_earnings - commission_total - gateway_fees
        
        return {
            'total_rides': total_rides,
            'gross_earnings': gross_earnings,
            'commission_deducted': commission_total,
            'gateway_fees_deducted': gateway_fees,
            'net_earnings': net_earnings,
            'rides': rides
        }
    
    def create_payout(self, driver, period_start, period_end, 
                     payout_method: str = 'bank_transfer') -> DriverPayout:
        """Create a driver payout"""
        
        earnings_data = self.calculate_driver_earnings(driver, period_start, period_end)
        
        if earnings_data['net_earnings'] <= 0:
            raise ValueError("No earnings available for payout")
        
        # Get default currency
        currency = Currency.objects.filter(is_default=True).first()
        
        with transaction.atomic():
            payout = DriverPayout.objects.create(
                driver=driver,
                payout_method=payout_method,
                gross_earnings=earnings_data['gross_earnings'],
                commission_deducted=earnings_data['commission_deducted'],
                gateway_fees_deducted=earnings_data['gateway_fees_deducted'],
                net_payout_amount=earnings_data['net_earnings'],
                currency=currency,
                period_start=period_start,
                period_end=period_end,
                scheduled_date=timezone.now()
            )
            
            # Associate rides and payments
            payout.rides.set(earnings_data['rides'])
            
            # Process payout through gateway if supported
            if driver.payout_gateway and driver.payout_recipient_id:
                try:
                    gateway = self.payment_processor.get_gateway(
                        driver.payout_gateway.gateway_type
                    )
                    
                    if gateway.supports_payouts():
                        response = gateway.create_payout(
                            driver.payout_recipient_id,
                            payout.net_payout_amount,
                            currency.code,
                            {'driver_id': str(driver.id), 'payout_id': str(payout.id)}
                        )
                        
                        if response.success:
                            payout.gateway_payout_id = response.transaction_id
                            payout.status = DriverPayout.PayoutStatus.PROCESSING
                            payout.processed_date = timezone.now()
                        else:
                            payout.status = DriverPayout.PayoutStatus.FAILED
                            payout.failure_reason = response.message
                        
                        payout.save()
                
                except Exception as e:
                    logger.error(f"Payout processing failed: {e}")
                    payout.status = DriverPayout.PayoutStatus.FAILED
                    payout.failure_reason = str(e)
                    payout.save()
            
            return payout


class DisputeService:
    """Payment dispute management"""
    
    def create_dispute(self, payment: Payment, reason: str, 
                      customer_message: str = None) -> PaymentDispute:
        """Create a payment dispute"""
        
        dispute = PaymentDispute.objects.create(
            payment=payment,
            dispute_reason=reason,
            disputed_amount=payment.amount,
            currency=payment.currency,
            dispute_date=timezone.now(),
            customer_message=customer_message or ''
        )
        
        # Update payment status
        payment.status = Payment.PaymentStatus.DISPUTED
        payment.save()
        
        # Log audit
        PaymentAuditLog.objects.create(
            action_type=PaymentAuditLog.ActionType.DISPUTE_CREATED,
            description=f"Dispute created for payment {payment.id}",
            payment=payment,
            dispute=dispute,
            user=payment.user
        )
        
        return dispute
    
    def resolve_dispute(self, dispute: PaymentDispute, outcome: str, 
                       resolution_amount: Decimal = None) -> bool:
        """Resolve a payment dispute"""
        
        dispute.resolution_outcome = outcome
        dispute.resolved_date = timezone.now()
        dispute.resolution_amount = resolution_amount
        
        if outcome == 'resolved_won':
            dispute.status = PaymentDispute.DisputeStatus.RESOLVED_WON
            # Keep payment as succeeded
        elif outcome == 'resolved_lost':
            dispute.status = PaymentDispute.DisputeStatus.RESOLVED_LOST
            # Process refund if needed
            if resolution_amount:
                processor = PaymentProcessor()
                processor.process_refund(
                    dispute.payment, 
                    resolution_amount, 
                    "Dispute resolution"
                )
        
        dispute.save()
        return True
