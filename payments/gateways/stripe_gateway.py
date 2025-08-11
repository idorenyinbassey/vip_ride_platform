# payments/gateways/stripe_gateway.py
"""
Stripe payment gateway integration
"""

import stripe
from decimal import Decimal
from typing import Dict, List
from .base import BasePaymentGateway, PaymentGatewayResponse
import logging

logger = logging.getLogger(__name__)


class StripeGateway(BasePaymentGateway):
    """Stripe payment gateway implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        stripe.api_key = self.secret_key
        self.publishable_key = config.get('publishable_key')
    
    def get_gateway_name(self) -> str:
        return "Stripe"
    
    def get_supported_currencies(self) -> List[str]:
        return [
            'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 
            'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'BGN', 'RON', 'HRK',
            'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN', 'UYU', 'NGN'
        ]
    
    def create_payment_intent(self, amount: Decimal, currency: str, 
                            metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a Stripe PaymentIntent"""
        try:
            amount_in_cents = self.format_amount(amount, currency)
            
            payment_intent_data = {
                'amount': amount_in_cents,
                'currency': currency.lower(),
                'automatic_payment_methods': {'enabled': True}
            }
            
            if metadata:
                payment_intent_data['metadata'] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            
            return PaymentGatewayResponse(
                success=True,
                transaction_id=payment_intent.id,
                reference=payment_intent.id,
                message='PaymentIntent created successfully',
                raw_response=payment_intent,
                amount=amount,
                metadata={
                    'client_secret': payment_intent.client_secret,
                    'status': payment_intent.status
                }
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Stripe error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Gateway error: {str(e)}"
            )
    
    def capture_payment(self, payment_intent_id: str, 
                       amount: Decimal = None) -> PaymentGatewayResponse:
        """Capture a Stripe PaymentIntent"""
        try:
            # Get the payment intent first to get its currency
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            currency = payment_intent.currency.upper()
            
            capture_data = {}
            if amount:
                capture_data['amount_to_capture'] = self.format_amount(amount, currency)
            
            payment_intent = stripe.PaymentIntent.capture(
                payment_intent_id, 
                **capture_data
            )
            
            if payment_intent.status == 'succeeded':
                amount = self.parse_amount(payment_intent.amount, payment_intent.currency)
                
                # Calculate Stripe fee from latest charge
                charges = payment_intent.charges.data
                stripe_fee = Decimal('0')
                if charges:
                    balance_transaction_id = charges[0].balance_transaction
                    if balance_transaction_id:
                        balance_transaction = stripe.BalanceTransaction.retrieve(
                            balance_transaction_id
                        )
                        stripe_fee = self.parse_amount(
                            balance_transaction.fee, 
                            payment_intent.currency
                        )
                
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=payment_intent.id,
                    reference=payment_intent.id,
                    message='Payment captured successfully',
                    raw_response=payment_intent,
                    amount=amount,
                    fee=stripe_fee
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    transaction_id=payment_intent_id,
                    message=f'Payment capture failed: {payment_intent.status}'
                )
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe capture error: {e}")
            return PaymentGatewayResponse(
                success=False,
                transaction_id=payment_intent_id,
                message=f"Capture failed: {str(e)}"
            )
    
    def get_payment_status(self, transaction_id: str) -> PaymentGatewayResponse:
        """Get payment status from Stripe"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
            
            amount = self.parse_amount(payment_intent.amount, payment_intent.currency)
            
            success = payment_intent.status == 'succeeded'
            
            return PaymentGatewayResponse(
                success=success,
                transaction_id=payment_intent.id,
                reference=payment_intent.id,
                message=f'Payment status: {payment_intent.status}',
                raw_response=payment_intent,
                amount=amount,
                metadata={'status': payment_intent.status}
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe status error: {e}")
            return PaymentGatewayResponse(
                success=False,
                transaction_id=transaction_id,
                message=f"Status check failed: {str(e)}"
            )
    
    def refund_payment(self, transaction_id: str, 
                      amount: Decimal = None, reason: str = None) -> PaymentGatewayResponse:
        """Create a refund on Stripe"""
        try:
            refund_data = {
                'payment_intent': transaction_id
            }
            
            if amount:
                # Get the currency from the original payment intent
                payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
                refund_data['amount'] = self.format_amount(amount, payment_intent.currency)
            
            if reason:
                refund_data['reason'] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            if refund.status in ['succeeded', 'pending']:
                refund_amount = self.parse_amount(refund.amount, refund.currency)
                
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=refund.id,
                    reference=refund.payment_intent,
                    message=f'Refund {refund.status}',
                    raw_response=refund,
                    amount=refund_amount
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=f'Refund failed: {refund.status}',
                    raw_response=refund
                )
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Refund failed: {str(e)}"
            )
    
    def supports_payouts(self) -> bool:
        return True
    
    def supports_disputes(self) -> bool:
        return True
    
    def create_payout(self, recipient_id: str, amount: Decimal, 
                     currency: str, metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a payout (transfer) on Stripe"""
        try:
            payout_data = {
                'amount': self.format_amount(amount, currency),
                'currency': currency.lower(),
                'method': 'instant'  # or 'standard'
            }
            
            if metadata:
                payout_data['metadata'] = metadata
            
            payout = stripe.Payout.create(**payout_data)
            
            return PaymentGatewayResponse(
                success=True,
                transaction_id=payout.id,
                reference=payout.id,
                message=f'Payout {payout.status}',
                raw_response=payout,
                amount=self.parse_amount(payout.amount, payout.currency)
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payout error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Payout failed: {str(e)}"
            )
    
    def create_customer(self, email: str, name: str = None, 
                       phone: str = None, metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a customer on Stripe"""
        try:
            customer_data = {'email': email}
            
            if name:
                customer_data['name'] = name
            if phone:
                customer_data['phone'] = phone
            if metadata:
                customer_data['metadata'] = metadata
            
            customer = stripe.Customer.create(**customer_data)
            
            return PaymentGatewayResponse(
                success=True,
                transaction_id=customer.id,
                reference=customer.id,
                message='Customer created successfully',
                raw_response=customer,
                metadata={
                    'customer_id': customer.id,
                    'email': customer.email
                }
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Customer creation failed: {str(e)}"
            )
    
    def tokenize_payment_method(self, payment_data: Dict) -> PaymentGatewayResponse:
        """Create a payment method on Stripe"""
        try:
            payment_method = stripe.PaymentMethod.create(**payment_data)
            
            return PaymentGatewayResponse(
                success=True,
                transaction_id=payment_method.id,
                reference=payment_method.id,
                message='Payment method created successfully',
                raw_response=payment_method,
                metadata={
                    'payment_method_id': payment_method.id,
                    'type': payment_method.type
                }
            )
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment method error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Payment method creation failed: {str(e)}"
            )
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except (ValueError, stripe.error.SignatureVerificationError):
            return False
