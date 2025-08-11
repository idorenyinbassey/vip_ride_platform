# payments/gateways/base.py
"""
Base payment gateway interface for multi-gateway support
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PaymentGatewayError(Exception):
    """Base exception for payment gateway errors"""
    pass


class PaymentGatewayResponse:
    """Standardized response from payment gateways"""
    
    def __init__(self, success: bool, transaction_id: str = None, 
                 reference: str = None, message: str = None, 
                 raw_response: Dict = None, amount: Decimal = None,
                 fee: Decimal = None, metadata: Dict = None):
        self.success = success
        self.transaction_id = transaction_id
        self.reference = reference
        self.message = message
        self.raw_response = raw_response or {}
        self.amount = amount
        self.fee = fee
        self.metadata = metadata or {}
    
    def __str__(self):
        return f"PaymentResponse(success={self.success}, id={self.transaction_id}, message='{self.message}')"


class BasePaymentGateway(ABC):
    """Base class for all payment gateway integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_test_mode = config.get('test_mode', True)
        self.api_key = config.get('api_key')
        self.secret_key = config.get('secret_key')
        self.webhook_secret = config.get('webhook_secret')
        
        if not self.api_key:
            raise PaymentGatewayError("API key is required")
    
    @abstractmethod
    def get_gateway_name(self) -> str:
        """Return the name of the gateway"""
        pass
    
    @abstractmethod
    def get_supported_currencies(self) -> List[str]:
        """Return list of supported currency codes"""
        pass
    
    @abstractmethod
    def create_payment_intent(self, amount: Decimal, currency: str, 
                            metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a payment intent"""
        pass
    
    @abstractmethod
    def capture_payment(self, payment_intent_id: str, 
                       amount: Decimal = None) -> PaymentGatewayResponse:
        """Capture a payment"""
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, 
                      amount: Decimal = None, reason: str = None) -> PaymentGatewayResponse:
        """Refund a payment"""
        pass
    
    @abstractmethod
    def get_payment_status(self, transaction_id: str) -> PaymentGatewayResponse:
        """Get payment status"""
        pass
    
    def supports_payouts(self) -> bool:
        """Check if gateway supports payouts"""
        return False
    
    def supports_disputes(self) -> bool:
        """Check if gateway supports dispute handling"""
        return False
    
    def create_payout(self, recipient_id: str, amount: Decimal, 
                     currency: str, metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a payout (if supported)"""
        raise NotImplementedError("Payouts not supported by this gateway")
    
    def create_customer(self, email: str, name: str = None, 
                       phone: str = None, metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a customer"""
        raise NotImplementedError("Customer creation not implemented")
    
    def tokenize_payment_method(self, payment_data: Dict) -> PaymentGatewayResponse:
        """Tokenize payment method for future use"""
        raise NotImplementedError("Payment method tokenization not implemented")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        return True  # Override in specific implementations
    
    def calculate_fee(self, amount: Decimal) -> Decimal:
        """Calculate gateway fee for amount"""
        percentage_fee = self.config.get('percentage_fee', Decimal('2.9'))
        fixed_fee = self.config.get('fixed_fee', Decimal('0.00'))
        
        return (amount * percentage_fee / 100) + fixed_fee
    
    def format_amount(self, amount: Decimal, currency: str) -> int:
        """Format amount for gateway (usually in smallest currency unit)"""
        # Most gateways expect amounts in cents/kobo/paise
        if currency.upper() in ['NGN', 'KES', 'GHS', 'UGX', 'TZS']:
            return int(amount * 100)
        elif currency.upper() in ['JPY', 'KRW']:
            return int(amount)  # No decimal places
        else:
            return int(amount * 100)  # Default to cents
    
    def parse_amount(self, amount: int, currency: str) -> Decimal:
        """Parse amount from gateway response"""
        if currency.upper() in ['JPY', 'KRW']:
            return Decimal(str(amount))
        else:
            return Decimal(str(amount)) / 100
    
    def log_transaction(self, action: str, response: PaymentGatewayResponse, 
                       additional_data: Dict = None):
        """Log transaction for audit purposes"""
        log_data = {
            'gateway': self.get_gateway_name(),
            'action': action,
            'success': response.success,
            'transaction_id': response.transaction_id,
            'message': response.message,
            'test_mode': self.is_test_mode
        }
        
        if additional_data:
            log_data.update(additional_data)
        
        if response.success:
            logger.info(f"Payment gateway {action} successful", extra=log_data)
        else:
            logger.error(f"Payment gateway {action} failed", extra=log_data)
