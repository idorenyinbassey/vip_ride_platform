# Payment Processing Service for Premium Digital Cards
"""
Payment service for handling Stripe, Google Pay, Flutterwave, and Paystack transactions
for Premium Digital Card purchases
"""

import stripe
import requests
import logging
from decimal import Decimal
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from typing import Dict, Any, Optional

# Import payment libraries
try:
    from flutterwave import Rave
except ImportError:
    Rave = None

try:
    from pypaystack2 import Paystack
except ImportError:
    Paystack = None

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class PaymentError(Exception):
    """Custom exception for payment processing errors"""
    pass

class PremiumCardPaymentService:
    """Service for processing Premium Digital Card payments"""
    
    SUPPORTED_PAYMENT_METHODS = ['stripe', 'google_pay', 'paypal', 'flutterwave', 'paystack']
    
    @staticmethod
    def process_payment(
        payment_method: str,
        amount: Decimal,
        currency: str = 'usd',
        card_tier: str = 'premium',
        customer_email: str = '',
        payment_token: Optional[str] = None,
        payment_intent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process payment for Premium Digital Card
        
        Args:
            payment_method: Payment method (stripe, google_pay, paypal)
            amount: Payment amount in dollars
            currency: Payment currency (default: usd)
            card_tier: Tier of the card (premium, vip)
            customer_email: Customer email
            payment_token: Payment token from frontend
            payment_intent_id: Stripe Payment Intent ID
            
        Returns:
            Dict containing payment result and transaction details
        """
        
        if payment_method not in PremiumCardPaymentService.SUPPORTED_PAYMENT_METHODS:
            raise PaymentError(f"Unsupported payment method: {payment_method}")
        
        try:
            if payment_method == 'stripe':
                return PremiumCardPaymentService._process_stripe_payment(
                    amount=amount,
                    currency=currency,
                    customer_email=customer_email,
                    card_tier=card_tier,
                    payment_token=payment_token,
                    payment_intent_id=payment_intent_id
                )
            
            elif payment_method == 'google_pay':
                return PremiumCardPaymentService._process_google_pay_payment(
                    amount=amount,
                    currency=currency,
                    customer_email=customer_email,
                    card_tier=card_tier,
                    payment_token=payment_token
                )
            
            elif payment_method == 'paypal':
                return PremiumCardPaymentService._process_paypal_payment(
                    amount=amount,
                    currency=currency,
                    customer_email=customer_email,
                    card_tier=card_tier,
                    payment_token=payment_token
                )
                
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            raise PaymentError(f"Payment processing failed: {str(e)}")
    
    @staticmethod
    def _process_stripe_payment(
        amount: Decimal,
        currency: str,
        customer_email: str,
        card_tier: str,
        payment_token: Optional[str] = None,
        payment_intent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process Stripe payment"""
        
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            @staticmethod
            def process_payment(
                payment_method: str,
                amount: Decimal,
                currency: str = 'usd',
                card_tier: str = 'premium',
                customer_email: str = '',
                payment_token: Optional[str] = None,
                payment_intent_id: Optional[str] = None
            ) -> Dict[str, Any]:
                """
                Process payment for Premium Digital Card
                ...existing code...
                try:
                    if payment_method == 'stripe':
                        return PremiumCardPaymentService._process_stripe_payment(
                            amount=amount,
                            currency=currency,
                            customer_email=customer_email,
                            card_tier=card_tier,
                            payment_token=payment_token,
                            payment_intent_id=payment_intent_id
                        )
                    elif payment_method == 'google_pay':
                        return PremiumCardPaymentService._process_google_pay_payment(
                            amount=amount,
                            currency=currency,
                            customer_email=customer_email,
                            card_tier=card_tier,
                            payment_token=payment_token
                        )
                    elif payment_method == 'flutterwave':
                        return PremiumCardPaymentService._process_flutterwave_payment(
                            amount=amount,
                            currency=currency,
                            customer_email=customer_email,
                            card_tier=card_tier,
                            payment_token=payment_token
                        )
                    elif payment_method == 'paystack':
                        return PremiumCardPaymentService._process_paystack_payment(
                            amount=amount,
                            currency=currency,
                            customer_email=customer_email,
                            card_tier=card_tier,
                            payment_token=payment_token
                        )
                    elif payment_method == 'paypal':
                        return PremiumCardPaymentService._process_paypal_payment(
                            amount=amount,
                            currency=currency,
                            customer_email=customer_email,
                            card_tier=card_tier,
                            payment_token=payment_token
                        )
                except Exception as e:
                    logger.error(f"Payment processing failed: {str(e)}")
                    raise PaymentError(f"Payment processing failed: {str(e)}")
    @staticmethod
    def _process_flutterwave_payment(
        amount: Decimal,
        currency: str,
        customer_email: str,
        card_tier: str,
        payment_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process Flutterwave payment using python-flutterwave"""
        if Rave is None:
            raise PaymentError("Flutterwave package not installed")
            
        try:
            rave = Rave(
                getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', ''),
                getattr(settings, 'FLUTTERWAVE_SECRET_KEY', ''),
                production=getattr(settings, 'FLUTTERWAVE_PRODUCTION', False)
            )
            
            # payment_token is expected to be a transaction reference from frontend
            res = rave.Card.verify(payment_token)
            
            if res['status'] == 'success' and res['data']['status'] == 'successful':
                return {
                    'success': True,
                    'transaction_id': res['data']['tx_ref'],
                    'payment_method': 'flutterwave',
                    'amount': float(amount),
                    'currency': currency,
                    'status': 'completed',
                    'receipt_url': None
                }
            else:
                raise PaymentError(f"Flutterwave payment failed: {res}")
                
        except Exception as e:
            logger.error(f"Flutterwave payment error: {str(e)}")
            raise PaymentError(f"Flutterwave error: {str(e)}")

    @staticmethod
    def _process_paystack_payment(
        amount: Decimal,
        currency: str,
        customer_email: str,
        card_tier: str,
        payment_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process Paystack payment using pypaystack2"""
        if Paystack is None:
            raise PaymentError("Paystack package not installed")
            
        try:
            paystack = Paystack(secret_key=getattr(settings, 'PAYSTACK_SECRET_KEY', ''))
            
            # payment_token is expected to be a Paystack reference from frontend
            res = paystack.transaction.verify(payment_token)
            
            if res['status'] and res['data']['status'] == 'success':
                return {
                    'success': True,
                    'transaction_id': res['data']['reference'],
                    'payment_method': 'paystack',
                    'amount': float(amount),
                    'currency': currency,
                    'status': 'completed',
                    'receipt_url': None
                }
            else:
                raise PaymentError(f"Paystack payment failed: {res}")
                
        except Exception as e:
            logger.error(f"Paystack payment error: {str(e)}")
            raise PaymentError(f"Paystack error: {str(e)}")
        currency: str,
        customer_email: str,
        card_tier: str,
        payment_token: str
    ) -> Dict[str, Any]:
        """Process Google Pay payment through Stripe"""
        
        try:
            # Google Pay tokens are processed through Stripe
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                payment_method_data={
                    'type': 'card',
                    'card': {
                        'token': payment_token
                    }
                },
                confirm=True,
                receipt_email=customer_email,
                description=f"Premium Digital Card - {card_tier.title()} Tier (Google Pay)",
                metadata={
                    'card_tier': card_tier,
                    'customer_email': customer_email,
                    'product': 'premium_digital_card',
                    'payment_method': 'google_pay'
                }
            )
            
            if payment_intent.status == 'succeeded':
                return {
                    'success': True,
                    'transaction_id': payment_intent.id,
                    'payment_method': 'google_pay',
                    'amount': float(amount),
                    'currency': currency,
                    'status': 'completed',
                    'receipt_url': payment_intent.charges.data[0].receipt_url if payment_intent.charges.data else None
                }
            else:
                raise PaymentError(f"Google Pay payment failed with status: {payment_intent.status}")
                
        except stripe.error.StripeError as e:
            raise PaymentError(f"Google Pay payment error: {str(e)}")
    
    @staticmethod
    def _process_paypal_payment(
        amount: Decimal,
        currency: str,
        customer_email: str,
        card_tier: str,
        payment_token: str
    ) -> Dict[str, Any]:
        """Process PayPal payment (placeholder implementation)"""
        
        # This would integrate with PayPal SDK
        # For now, return success for demonstration
        logger.info(f"PayPal payment processed for {customer_email}: ${amount}")
        
        return {
            'success': True,
            'transaction_id': f'paypal_{payment_token}',
            'payment_method': 'paypal',
            'amount': float(amount),
            'currency': currency,
            'status': 'completed',
            'receipt_url': None
        }
    
    @staticmethod
    def create_stripe_payment_intent(
        amount: Decimal,
        currency: str = 'usd',
        customer_email: str = '',
        card_tier: str = 'premium'
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent for frontend
        This allows the frontend to handle the payment securely
        """
        
        try:
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                automatic_payment_methods={'enabled': True},
                receipt_email=customer_email,
                description=f"Premium Digital Card - {card_tier.title()} Tier",
                metadata={
                    'card_tier': card_tier,
                    'customer_email': customer_email,
                    'product': 'premium_digital_card'
                }
            )
            
            return {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': amount_cents,
                'currency': currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Payment Intent: {str(e)}")
            raise PaymentError(f"Failed to create Payment Intent: {str(e)}")
    
    @staticmethod
    def verify_payment_status(transaction_id: str, payment_method: str) -> Dict[str, Any]:
        """Verify payment status by transaction ID"""
        
        try:
            if payment_method == 'stripe' or payment_method == 'google_pay':
                payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
                
                return {
                    'transaction_id': payment_intent.id,
                    'status': payment_intent.status,
                    'amount': payment_intent.amount / 100,  # Convert cents to dollars
                    'currency': payment_intent.currency,
                    'payment_method': payment_method,
                    'verified': payment_intent.status == 'succeeded'
                }
            
            elif payment_method == 'paypal':
                # PayPal verification would go here
                return {
                    'transaction_id': transaction_id,
                    'status': 'succeeded',
                    'verified': True,
                    'payment_method': 'paypal'
                }
                
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return {
                'transaction_id': transaction_id,
                'status': 'failed',
                'verified': False,
                'error': str(e)
            }
