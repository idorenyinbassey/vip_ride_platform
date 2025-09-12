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
    """Purchase premium digital cards"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            tier = data.get('tier', 'vip')
            
            if tier not in ['vip', 'vip_premium']:
                return Response({
                    'success': False,
                    'error': 'Invalid tier. Choose vip or vip_premium.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            payment_service = PremiumCardPaymentService()
            
            # Create payment intent
            amount = 299 if tier == 'vip' else 599  # Price in dollars
            
            try:
                payment_intent = payment_service.create_payment_intent(
                    amount=amount * 100,  # Convert to cents
                    currency='usd',
                    metadata={
                        'user_id': str(user.id),
                        'tier': tier,
                        'type': 'premium_card_purchase'
                    }
                )
                
                # Create pending card
                card = PremiumDigitalCard.objects.create(
                    tier=tier,
                    status='pending',
                    price=amount,
                    payment_intent_id=payment_intent['id']
                )
                
                return Response({
                    'success': True,
                    'payment_intent': {
                        'id': payment_intent['id'],
                        'client_secret': payment_intent['client_secret'],
                        'amount': amount,
                        'currency': 'usd'
                    },
                    'card': {
                        'id': str(card.id),
                        'tier': card.tier,
                        'price': card.price
                    }
                })
                
            except PaymentError as e:
                logger.error(f"Payment error for user {user.email}: {str(e)}")
                return Response({
                    'success': False,
                    'error': 'Payment processing failed. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Card purchase error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Card purchase failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PremiumCardActivationView(APIView):
    """Activate premium digital cards (legacy)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            card_number = data.get('card_number', '').replace('-', '').replace(' ', '')
            verification_code = data.get('verification_code', '')
            
            if not card_number or not verification_code:
                return Response({
                    'success': False,
                    'error': 'Card number and verification code are required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find the card
            try:
                card = PremiumDigitalCard.objects.get(
                    card_number=card_number,
                    verification_code=verification_code,
                    status__in=['available', 'sold']
                )
            except PremiumDigitalCard.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid card number or verification code.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if already activated by someone else
            if card.status == 'active' and card.owner != request.user:
                return Response({
                    'success': False,
                    'error': 'This card has already been activated by another user.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Activate the card
            with transaction.atomic():
                activation_success = card.activate_card(
                    user=request.user,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', 'Web'),
                    method='web'
                )
                
                if not activation_success:
                    return Response({
                        'success': False,
                        'error': 'Card activation failed. Please try again.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info(f"Premium card activated by user {request.user.email}")
            
            return Response({
                'success': True,
                'message': f'Premium card activated successfully! You have been upgraded to {card.tier.upper()} tier.',
                'card': {
                    'id': str(card.id),
                    'tier': card.tier,
                    'activated_at': card.activated_at,
                    'expires_at': card.expires_at
                },
                'user': {
                    'tier': request.user.tier,
                    'updated_at': timezone.now()
                }
            })
            
        except Exception as e:
            logger.error(f"Card activation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Card activation failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PremiumCardListView(APIView):
    """List user's premium cards"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        cards = PremiumDigitalCard.objects.filter(owner=user).values(
            'id', 'tier', 'status', 'activated_at', 'expires_at', 'card_number'
        )
        
        return Response({
            'cards': list(cards),
            'total': len(cards)
        })


class PaymentIntentView(APIView):
    """Create payment intent for premium card purchase"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            tier = data.get('tier', 'vip')
            
            if tier not in ['vip', 'vip_premium']:
                return Response({
                    'error': 'Invalid tier'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            amount = 299 if tier == 'vip' else 599
            payment_service = PremiumCardPaymentService()
            
            payment_intent = payment_service.create_payment_intent(
                amount=amount * 100,
                currency='usd',
                metadata={
                    'user_id': str(request.user.id),
                    'tier': tier
                }
            )
            
            return Response({
                'client_secret': payment_intent['client_secret'],
                'amount': amount
            })
            
        except Exception as e:
            logger.error(f"Payment intent error: {str(e)}")
            return Response({
                'error': 'Failed to create payment intent'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_premium_status(request):
    """Get user's premium status and active cards"""
    user = request.user
    
    # Get active premium card
    active_card = PremiumDigitalCard.objects.filter(
        owner=user,
        status='active'
    ).first()
    
    if active_card:
        return Response({
            'has_premium': True,
            'tier': user.tier,
            'active_card': {
                'id': str(active_card.id),
                'tier': active_card.tier,
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


# Flutter Integration Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def activate_premium_card(request):
    """
    Activate premium card for Flutter users - Auto-upgrades user tier
    
    Expected payload:
    {
        "card_number": "4532123456789012",
        "verification_code": "12345678",
        "device_name": "iPhone 12"  # Optional
    }
    """
    try:
        from .models import TrustedDevice
        from .utils import get_device_fingerprint, get_client_ip
        
        data = request.data
        card_number = data.get('card_number', '').replace('-', '').replace(' ', '')
        verification_code = data.get('verification_code', '')
        device_name = data.get('device_name', 'Flutter Mobile App')
        
        if not card_number or not verification_code:
            return Response({
                'success': False,
                'error': 'Card number and verification code are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find the card
        try:
            card = PremiumDigitalCard.objects.get(
                card_number=card_number,
                verification_code=verification_code,
                status='available'
            )
        except PremiumDigitalCard.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid card number or verification code, or card already activated.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if card is already owned by someone else
        if card.owner and card.owner != request.user:
            return Response({
                'success': False,
                'error': 'This card is already owned by another user.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Activate the card
        with transaction.atomic():
            # Assign card to user if not already assigned
            if not card.owner:
                card.owner = request.user
                card.status = 'sold'
                card.purchased_at = timezone.now()
                card.save()
            
            # Activate the card (this automatically updates user tier)
            activation_success = card.activate_card(
                user=request.user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', 'Flutter App'),
                method='mobile_app'
            )
            
            if not activation_success:
                return Response({
                    'success': False,
                    'error': 'Card activation failed. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Register/update device as trusted
            device_fp = get_device_fingerprint(request)
            device, created = TrustedDevice.objects.get_or_create(
                user=request.user,
                device_fingerprint=device_fp,
                defaults={
                    'device_name': device_name,
                    'user_agent': request.META.get('HTTP_USER_AGENT', 'Flutter App'),
                    'ip_address': get_client_ip(request),
                    'trust_level': 'vip' if card.tier in ['vip', 'vip_premium'] else 'basic',
                    'is_active': True
                }
            )
            
            if not created:
                device.last_used_at = timezone.now()
                device.usage_count += 1
                device.trust_level = 'vip' if card.tier in ['vip', 'vip_premium'] else 'basic'
                device.save()
            
            # Refresh user from database to get updated tier
            request.user.refresh_from_db()
        
        # Prepare response with updated user information
        try:
            from .rbac_settings import USER_TIER_SETTINGS
        except ImportError:
            # Fallback tier configuration
            USER_TIER_SETTINGS = {
                'regular': {
                    'require_mfa': False,
                    'permissions': ['basic_rides'],
                    'features': ['standard_booking']
                },
                'vip': {
                    'require_mfa': True,
                    'permissions': ['basic_rides', 'priority_booking', 'vip_support'],
                    'features': ['priority_rides', 'concierge_support']
                },
                'vip_premium': {
                    'require_mfa': True,
                    'permissions': ['basic_rides', 'priority_booking', 'vip_support', 'hotel_booking'],
                    'features': ['priority_rides', 'concierge_support', 'hotel_partnerships', 'encrypted_tracking']
                }
            }
        tier_config = USER_TIER_SETTINGS.get(request.user.tier, {})
        
        response_data = {
            'success': True,
            'message': f'Premium card activated successfully! You have been upgraded to {card.tier.upper()} tier.',
            'card': {
                'id': str(card.id),
                'card_number': card.card_number,
                'tier': card.tier,
                'activated_at': card.activated_at.isoformat(),
                'expires_at': card.expires_at.isoformat(),
                'status': card.status
            },
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'tier': request.user.tier,
                'tier_display': request.user.tier.replace('_', ' ').title(),
                'updated_at': timezone.now().isoformat()
            },
            'tier_info': {
                'current_tier': request.user.tier,
                'requires_mfa': tier_config.get('require_mfa', False),
                'permissions': tier_config.get('permissions', []),
                'features': tier_config.get('features', [])
            },
            'device': {
                'id': str(device.id),
                'trusted': True,
                'trust_level': device.trust_level,
                'registered_at': device.first_used_at.isoformat()
            },
            'next_steps': {
                'requires_mfa_setup': tier_config.get('require_mfa', False),
                'should_refresh_session': True,
                'redirect_to': 'dashboard'  # Flutter can use this for navigation
            }
        }
        
        logger.info(f"Premium card activated successfully for user {request.user.email}, tier: {request.user.tier}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Card activation error for user {request.user.email}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Card activation failed due to server error. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_tier_status(request):
    """
    Get current user tier status and requirements
    This endpoint helps Flutter sync user state after tier changes
    """
    try:
        from .models import TrustedDevice
        from .utils import get_device_fingerprint
        
        user = request.user
        
        # Get user's premium cards
        active_cards = PremiumDigitalCard.objects.filter(
            owner=user,
            status='active'
        ).values('tier', 'activated_at', 'expires_at')
        
        # Get tier configuration
        try:
            from .rbac_settings import USER_TIER_SETTINGS
        except ImportError:
            # Fallback tier configuration if rbac_settings doesn't exist
            USER_TIER_SETTINGS = {
                'regular': {
                    'require_mfa': False,
                    'permissions': ['basic_rides'],
                    'features': ['standard_booking'],
                    'rate_limits': {'requests_per_minute': 60}
                },
                'vip': {
                    'require_mfa': True,
                    'mfa_methods': ['totp', 'email'],
                    'permissions': ['basic_rides', 'priority_booking', 'vip_support'],
                    'features': ['priority_rides', 'concierge_support'],
                    'rate_limits': {'requests_per_minute': 120}
                },
                'vip_premium': {
                    'require_mfa': True,
                    'mfa_methods': ['totp', 'email'],
                    'permissions': ['basic_rides', 'priority_booking', 'vip_support', 'hotel_booking'],
                    'features': ['priority_rides', 'concierge_support', 'hotel_partnerships', 'encrypted_tracking'],
                    'rate_limits': {'requests_per_minute': 200}
                }
            }
        tier_config = USER_TIER_SETTINGS.get(user.tier, {})
        
        # Check device trust status
        device_fp = get_device_fingerprint(request)
        trusted_device = TrustedDevice.objects.filter(
            user=user,
            device_fingerprint=device_fp,
            is_active=True
        ).first()
        
        response_data = {
            'user': {
                'id': user.id,
                'email': user.email,
                'tier': user.tier,
                'tier_display': user.tier.replace('_', ' ').title(),
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'tier_info': {
                'current_tier': user.tier,
                'requires_mfa': tier_config.get('require_mfa', False),
                'mfa_methods': tier_config.get('mfa_methods', ['totp', 'email']),
                'permissions': tier_config.get('permissions', []),
                'features': tier_config.get('features', []),
                'rate_limits': tier_config.get('rate_limits', {})
            },
            'premium_cards': {
                'total': len(active_cards),
                'active_cards': list(active_cards)
            },
            'device': {
                'fingerprint': device_fp,
                'is_trusted': trusted_device is not None,
                'trust_level': trusted_device.trust_level if trusted_device else None,
                'last_used': trusted_device.last_used_at.isoformat() if trusted_device else None
            },
            'session': {
                'valid': True,
                'last_updated': timezone.now().isoformat(),
                'requires_refresh': False
            },
            'requirements': {
                'mfa_required': tier_config.get('require_mfa', False),
                'device_trust_required': tier_config.get('require_device_trust', False),
                'session_timeout': tier_config.get('session_timeout', 3600)
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Tier status check error for user {request.user.email}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to retrieve tier status.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)