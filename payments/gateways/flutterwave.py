# payments/gateways/flutterwave.py
"""
Flutterwave payment gateway integration
"""

import requests
import hashlib
import hmac
from decimal import Decimal
from typing import Dict, List
from .base import BasePaymentGateway, PaymentGatewayResponse
import logging

logger = logging.getLogger(__name__)


class FlutterwaveGateway(BasePaymentGateway):
    """Flutterwave payment gateway implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.flutterwave.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def get_gateway_name(self) -> str:
        return "Flutterwave"
    
    def get_supported_currencies(self) -> List[str]:
        return ['NGN', 'USD', 'EUR', 'GBP', 'KES', 'UGX', 'ZAR', 'GHS']
    
    def create_payment_intent(self, amount: Decimal, currency: str, 
                            metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a Flutterwave payment link"""
        url = f"{self.base_url}/payments"
        
        metadata = metadata or {}
        
        payload = {
            'tx_ref': metadata.get('reference') or f"tx_{self._generate_ref()}",
            'amount': str(amount),
            'currency': currency.upper(),
            'redirect_url': metadata.get('redirect_url') or 'https://example.com',
            'customer': {
                'email': metadata.get('email', 'customer@example.com'),
                'name': metadata.get('name', 'Customer')
            },
            'customizations': {
                'title': 'VIP Ride Payment',
                'description': metadata.get('description', 'Ride payment')
            }
        }
        
        if metadata:
            payload['meta'] = metadata
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=data['data']['id'],
                    reference=payload['tx_ref'],
                    message=data.get('message', 'Payment link created'),
                    raw_response=data,
                    amount=amount,
                    metadata={'payment_link': data['data']['link']}
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=data.get('message', 'Payment creation failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Flutterwave API error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Network error: {str(e)}"
            )
    
    def capture_payment(self, payment_intent_id: str, 
                       amount: Decimal = None) -> PaymentGatewayResponse:
        """Verify a Flutterwave transaction"""
        return self.get_payment_status(payment_intent_id)
    
    def get_payment_status(self, transaction_id: str) -> PaymentGatewayResponse:
        """Verify transaction status with Flutterwave"""
        url = f"{self.base_url}/transactions/{transaction_id}/verify"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success' and data['data']['status'] == 'successful':
                amount = Decimal(str(data['data']['amount']))
                
                # Calculate Flutterwave fee
                app_fee = Decimal(str(data['data'].get('app_fee', 0)))
                
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=str(data['data']['id']),
                    reference=data['data']['tx_ref'],
                    message='Payment verified successfully',
                    raw_response=data,
                    amount=amount,
                    fee=app_fee,
                    metadata={
                        'processor_response': data['data']['processor_response'],
                        'payment_type': data['data']['payment_type'],
                        'created_at': data['data']['created_at']
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
            logger.error(f"Flutterwave verification error: {e}")
            return PaymentGatewayResponse(
                success=False,
                transaction_id=transaction_id,
                message=f"Verification failed: {str(e)}"
            )
    
    def refund_payment(self, transaction_id: str, 
                      amount: Decimal = None, reason: str = None) -> PaymentGatewayResponse:
        """Create a refund on Flutterwave"""
        url = f"{self.base_url}/transactions/{transaction_id}/refund"
        
        payload = {}
        
        if amount:
            payload['amount'] = str(amount)
        
        if reason:
            payload['comments'] = reason
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=str(data['data']['id']),
                    reference=data['data']['tx_ref'],
                    message=data.get('message', 'Refund processed successfully'),
                    raw_response=data,
                    amount=Decimal(str(data['data']['amount_refunded']))
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=data.get('message', 'Refund failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Flutterwave refund error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Refund failed: {str(e)}"
            )
    
    def supports_payouts(self) -> bool:
        return True
    
    def create_payout(self, recipient_id: str, amount: Decimal, 
                     currency: str, metadata: Dict = None) -> PaymentGatewayResponse:
        """Create a transfer (payout) on Flutterwave"""
        url = f"{self.base_url}/transfers"
        
        metadata = metadata or {}
        
        payload = {
            'account_bank': metadata.get('bank_code', '044'),
            'account_number': metadata.get('account_number'),
            'amount': str(amount),
            'currency': currency.upper(),
            'reference': metadata.get('reference', f"payout_{self._generate_ref()}"),
            'narration': metadata.get('narration', 'Driver payout'),
            'beneficiary_name': metadata.get('beneficiary_name', 'Driver')
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return PaymentGatewayResponse(
                    success=True,
                    transaction_id=str(data['data']['id']),
                    reference=data['data']['reference'],
                    message=data.get('message', 'Transfer initiated'),
                    raw_response=data,
                    amount=Decimal(str(data['data']['amount']))
                )
            else:
                return PaymentGatewayResponse(
                    success=False,
                    message=data.get('message', 'Transfer failed'),
                    raw_response=data
                )
                
        except requests.RequestException as e:
            logger.error(f"Flutterwave transfer error: {e}")
            return PaymentGatewayResponse(
                success=False,
                message=f"Transfer failed: {str(e)}"
            )
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Flutterwave webhook signature using HMAC-SHA256"""
        if not self.webhook_secret:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def get_banks(self, country: str = 'NG') -> List[Dict]:
        """Get list of banks for transfer recipients"""
        url = f"{self.base_url}/banks/{country}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return data['data']
            else:
                return []
                
        except requests.RequestException as e:
            logger.error(f"Flutterwave banks fetch error: {e}")
            return []
    
    def _generate_ref(self) -> str:
        """Generate a unique reference"""
        import time
        import random
        return f"{int(time.time())}{random.randint(1000, 9999)}"
