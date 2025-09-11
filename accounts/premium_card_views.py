# Premium Digital Card Views
"""
API views for Premium Digital Card system
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import transaction
from .premium_card_models import PremiumDigitalCard, PremiumCardTransaction
from .payment_service import PremiumCardPaymentService, PaymentError
from .utils import get_client_ip
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class PremiumCardPurchaseView(APIView):
    """Purchase a Premium Digital Card"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Purchase Premium Digital Card with payment processing"""
        user = request.user
        
        # Get request data
        tier = request.data.get('tier', 'vip')
        payment_method = request.data.get('payment_method', 'stripe')
        payment_token = request.data.get('payment_token')
        payment_intent_id = request.data.get('payment_intent_id')
        
        if tier not in ['vip', 'vip_premium']:
            return Response(
                {'error': _('Invalid tier. Must be "vip" or "vip_premium".')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_method not in ['stripe', 'google_pay', 'flutterwave', 'paystack']:
            return Response(
                {'error': _('Invalid payment method.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine price
        price = 149.99 if tier == 'vip_premium' else 99.99
        
        try:
            with transaction.atomic():
                # Process payment first
                payment_result = PremiumCardPaymentService.process_payment(
                    payment_method=payment_method,
                    amount=price,
                    currency='usd',
                    card_tier=tier,
                    customer_email=user.email,
                    payment_token=payment_token,
                    payment_intent_id=payment_intent_id
                )
                
                if not payment_result.get('success'):
                    return Response(
                        {'error': _('Payment processing failed.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create card after successful payment
                card = PremiumDigitalCard.objects.create(
                    card_number=PremiumDigitalCard.generate_card_number(),
                    verification_code=PremiumDigitalCard.generate_verification_code(),
                    tier=tier,
                    status='sold',
                    owner=user,
                    purchased_at=timezone.now(),
                    price=price,
                    validity_months=18 if tier == 'vip_premium' else 12
                )
                
                # Update user tier immediately after purchase
                # This allows immediate access to premium features
                user.tier = tier
                user.save()
                
                # Create transaction record
                card_transaction = PremiumCardTransaction.objects.create(
                    card=card,
                    user=user,
                    amount=card.price,
                    payment_method=payment_method,
                    status='completed',
                    transaction_id=payment_result.get('transaction_id'),
                    completed_at=timezone.now()
                )
                
                logger.info(f"Premium card purchased: {card.card_number} by user {user.email}")
                
                return Response({
                    'message': _('Premium card purchased successfully!'),
                    'card': {
                        'id': str(card.id),
                        'card_number': card.card_number,
                        'tier': card.tier,
                        'status': card.status,
                        'price': float(card.price),
                        'validity_months': card.validity_months,
                        'purchased_at': card.purchased_at.isoformat(),
                    },
                    'transaction_id': str(card_transaction.id)
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Premium card purchase failed: {str(e)}")
            return Response(
                {'error': _('Failed to purchase premium card. Please try again.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentIntentView(APIView):
    """Create Stripe Payment Intent for Premium Card purchase"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create Payment Intent for secure payment processing"""
        user = request.user
        
        tier = request.data.get('tier', 'vip')
        
        if tier not in ['vip', 'vip_premium']:
            return Response(
                {'error': _('Invalid tier. Must be "vip" or "vip_premium".')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine price - vip_premium is the highest tier
        price = 149.99 if tier == 'vip_premium' else 99.99
        
        try:
            payment_intent_data = PremiumCardPaymentService.create_stripe_payment_intent(
                amount=price,
                currency='usd',
                customer_email=user.email,
                card_tier=tier
            )
            
            return Response({
                'client_secret': payment_intent_data['client_secret'],
                'payment_intent_id': payment_intent_data['payment_intent_id'],
                'amount': payment_intent_data['amount'] / 100,  # Convert cents to dollars
                'currency': payment_intent_data['currency'],
                'tier': tier
            }, status=status.HTTP_200_OK)
            
        except PaymentError as e:
            logger.error(f"Failed to create Payment Intent for user {user.email}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Payment Intent creation failed: {str(e)}")
            return Response(
                {'error': _('Failed to create payment intent. Please try again.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PremiumCardActivationView(APIView):
    """Activate Premium Digital Card using 8-digit verification code"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Activate premium card with verification code"""
        user = request.user
        verification_code = request.data.get('verification_code')
        
        if not verification_code:
            return Response(
                {'error': _('Verification code is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(verification_code) != 8 or not verification_code.isdigit():
            return Response(
                {'error': _('Verification code must be exactly 8 digits.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Find card with verification code
            card = PremiumDigitalCard.objects.get(
                verification_code=verification_code,
                owner=user,
                status='sold'
            )
            
            # Activate card
            client_ip = get_client_ip(request)
            card.activate_card(user, client_ip)
            
            logger.info(f"Premium card activated: {card.card_number} for user {user.email}")
            
            return Response({
                'message': _('Premium card activated successfully!'),
                'card': {
                    'id': str(card.id),
                    'card_number': card.card_number,
                    'tier': card.tier,
                    'status': card.status,
                    'activated_at': card.activated_at.isoformat(),
                    'expires_at': card.expires_at.isoformat(),
                    'days_until_expiry': card.days_until_expiry(),
                },
                'user_tier': user.tier
            }, status=status.HTTP_200_OK)
            
        except PremiumDigitalCard.DoesNotExist:
            return Response(
                {'error': _('Invalid verification code or card not found.')},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Premium card activation failed: {str(e)}")
            return Response(
                {'error': _('Failed to activate premium card. Please try again.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PremiumCardListView(APIView):
    """Get user's premium cards"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all premium cards for authenticated user"""
        user = request.user
        
        cards = PremiumDigitalCard.objects.filter(owner=user).order_by('-created_at')
        
        cards_data = []
        for card in cards:
            card_data = {
                'id': str(card.id),
                'card_number': card.card_number,
                'tier': card.tier,
                'status': card.status,
                'price': float(card.price),
                'validity_months': card.validity_months,
                'purchased_at': card.purchased_at.isoformat() if card.purchased_at else None,
                'activated_at': card.activated_at.isoformat() if card.activated_at else None,
                'expires_at': card.expires_at.isoformat() if card.expires_at else None,
                'days_until_expiry': card.days_until_expiry(),
                'is_active': card.is_active(),
            }
            
            # Only show verification code for sold (not yet activated) cards
            if card.status == 'sold':
                card_data['verification_code'] = card.verification_code
            
            cards_data.append(card_data)
        
        return Response({
            'cards': cards_data,
            'active_card_count': len([c for c in cards if c.is_active()]),
            'total_cards': cards.count()
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_premium_status(request):
    """Get user's current premium status"""
    user = request.user
    
    # Get active premium card
    active_card = PremiumDigitalCard.objects.filter(
        owner=user,
        status='active'
    ).first()
    
    if active_card and active_card.is_active():
        return Response({
            'has_premium': True,
            'tier': user.tier,
            'active_card': {
                'id': str(active_card.id),
                'card_number': active_card.card_number,
                'tier': active_card.tier,
                'expires_at': active_card.expires_at.isoformat(),
                'days_until_expiry': active_card.days_until_expiry(),
            }
        })
    else:
        return Response({
            'has_premium': False,
            'tier': user.tier,
            'active_card': None
        })
