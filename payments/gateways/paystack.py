# payments/gateways/paystack.py
"""
Paystack payment gateway integration
"""

import requests
import hashlib
import hmac
from decimal import Decimal
from typing import Dict, List
from .base import BasePaymentGateway, PaymentGatewayResponse, PaymentGatewayError
import logging

logger = logging.getLogger(__name__)


class PaystackGateway(BasePaymentGateway):
    """Paystack payment gateway implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.webhook_secret = config.get('webhook_secret')
        self.base_url = "https://api.paystack.co" if not self.is_test_mode else "https://api.paystack.co"
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def get_gateway_name(self) -> str:
        return "Paystack"
    
    def get_supported_currencies(self) -> List[str]:
        return ['NGN', 'USD', 'GHS', 'ZAR', 'KES']
    
    def create_payment_intent(self, amount: Decimal, currency: str, 
                            metadata: Dict = None) -> PaymentGatewayResponse:
        """Initialize a Paystack transaction"""
        url = f"{self.base_url}/transaction/initialize"
        
        # Convert amount to kobo for NGN, cents for others
        amount_in_subunit = self.format_amount(amount, currency)
        
        payload = {
            'amount': amount_in_subunit,
            'currency': currency.upper(),
            'metadata': metadata or {}
        }
        
        # Add email if provided in metadata (required by Paystack)
        if metadata and 'email' in metadata:
            payload['email'] = metadata['email']
        else:
            raise ValueError("Email is required for Paystack transactions")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status'):
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=data['data']['reference'],
                    reference=data['data']['reference'],
                    message=data.get('message', 'Transaction initialized'),
                    raw_response=data,
                    amount=amount,
                    metadata={'authorization_url': data['data']['authorization_url']}
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=data.get('message', 'Transaction initialization failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Paystack API error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Network error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Paystack error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Gateway error: {str(e)}"
            )
    
    def capture_payment(self, payment_intent_id: str, 
                       amount: Decimal = None) -> PaymentGatewayResponse:
        """Verify a Paystack transaction (equivalent to capture)"""
        return self.get_payment_status(payment_intent_id)
    
    def get_payment_status(self, transaction_id: str) -> PaymentGatewayResponse:
        """Verify transaction status with Paystack"""
        url = f"{self.base_url}/transaction/verify/{transaction_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') and data['data']['status'] == 'success':
                amount = self.parse_amount(
                    data['data']['amount'], 
                    data['data']['currency']
                )
                
                # Calculate Paystack fee
                fees = data['data'].get('fees', 0)
                gateway_fee = self.parse_amount(fees, data['data']['currency'])
                
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=data['data']['reference'],
                    reference=data['data']['reference'],
                    message='Payment verified successfully',
                    raw_response=data,
                    amount=amount,
                    fee=gateway_fee,
                    metadata={
                        'gateway_response': data['data']['gateway_response'],
                        'paid_at': data['data']['paid_at'],
                        'channel': data['data']['channel']
                    }
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    transaction_id=transaction_id,
                    message=data.get('message', 'Payment verification failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Paystack verification error: {e}")
            return PaymentGatewayResponse(
                success=False,
                transaction_id=transaction_id,
                message=f"Verification failed: {str(e)}"
            )
    
    def refund_payment(self, transaction_id: str, 
                      amount: Decimal = None, reason: str = None) -> PaymentGatewayResponse:
        """Create a refund on Paystack"""
        url = f"{self.base_url}/refund"
        
        payload = {
            'transaction': transaction_id
        }
        
        if amount:
            payload['amount'] = self.format_amount(amount, 'NGN')  # Default to NGN
        
        if reason:
            payload['merchant_note'] = reason
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status'):
                refund_data = data['data']
                
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=refund_data['id'],
                    reference=refund_data['transaction']['reference'],
                    message=data.get('message', 'Refund created successfully'),
                    raw_response=data,
                    amount=self.parse_amount(
                        refund_data['amount'], 
                        refund_data['currency']
                    )
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=data.get('message', 'Refund failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Paystack refund error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Refund failed: {str(e)}"
            )
    
    def supports_payouts(self) -> bool:
        return True
    
    def create_payout(self, recipient_id: str, amount: Decimal, 
                     currency: str, metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a transfer (payout) on Paystack"""
        url = f"{self.base_url}/transfer"
        
        payload = {
            'source': 'balance',
            'amount': self.format_amount(amount, currency),
            'recipient': recipient_id,
            'reason': metadata.get('reason', 'Driver payout') if metadata else 'Driver payout'
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status'):
                transfer_data = data['data']
                
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=transfer_data['transfer_code'],
                    reference=transfer_data['reference'],
                    message=data.get('message', 'Transfer initiated'),
                    raw_response=data,
                    amount=self.parse_amount(transfer_data['amount'], currency)
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=data.get('message', 'Transfer failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Paystack transfer error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Transfer failed: {str(e)}"
            )
    
    def create_transfer_recipient(self, account_number: str, bank_code: str, 
                                 name: str, currency: str = 'NGN') -> PaymentGatewayResponse:
        """Create a transfer recipient"""
        url = f"{self.base_url}/transferrecipient"
        
        payload = {
            'type': 'nuban',
            'name': name,
            'account_number': account_number,
            'bank_code': bank_code,
            'currency': currency
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status'):
                recipient_data = data['data']
                
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=recipient_data['recipient_code'],
                    reference=recipient_data['recipient_code'],
                    message='Transfer recipient created',
                    raw_response=data,
                    metadata={
                        'recipient_code': recipient_data['recipient_code'],
                        'account_number': recipient_data['details']['account_number'],
                        'bank_name': recipient_data['details']['bank_name']
                    }
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=data.get('message', 'Recipient creation failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Paystack recipient creation error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Recipient creation failed: {str(e)}"
            )
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Paystack webhook signature"""
        if not self.webhook_secret:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def get_banks(self, country: str = 'nigeria') -> List[Dict]:
        """Get list of banks for transfer recipients"""
        url = f"{self.base_url}/bank"
        params = {'country': country}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status'):
                return data['data']
            else:
                return []
                
        except requests.RequestException as e:
            logger.error(f"Paystack banks fetch error: {e}")
            return []
