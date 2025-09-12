# VIP Card API Views
"""
API views for VIP Digital Card system with Serial Number + Activation Code
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .vip_card_models import VIPDigitalCard
from .activation_history_models import CardActivationHistory
from .utils import get_client_ip
import logging
import re

User = get_user_model()
logger = logging.getLogger(__name__)


class VIPCardActivationView(APIView):
    """Activate VIP Digital Card using serial number and activation code"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Activate VIP card with automatic tier routing"""
        user = request.user
        serial_number = request.data.get('serial_number')
        activation_code = request.data.get('activation_code')
        
        if not serial_number or not activation_code:
            return Response(
                {'error': _('Both serial number and activation code are required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Format inputs
        serial_number = serial_number.strip().upper()
        activation_code = activation_code.strip().upper()
        
        try:
            # Find the card
            card = VIPDigitalCard.objects.get(
                serial_number=serial_number,
                activation_code=activation_code
            )
            
            # Check if card can be activated
            if not card.can_be_activated:
                if card.status == 'active':
                    return Response(
                        {'error': _('This card has already been activated.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif card.is_expired:
                    return Response(
                        {'error': _('This card has expired and cannot be activated.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    return Response(
                        {'error': _('This card cannot be activated at this time.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get client IP
            client_ip = get_client_ip(request)
            
            # Activate card (this automatically updates user tier)
            old_tier = user.tier
            card.activate_card(user, client_ip)
            
            # Refresh user from database to get updated tier
            user.refresh_from_db()
            
            logger.info(f"VIP card activated successfully: {card.serial_number} for user {user.email}, tier upgraded from {old_tier} to {user.tier}")
            
            return Response({
                'success': True,
                'message': _('VIP card activated successfully! Your account has been upgraded.'),
                'card': {
                    'id': str(card.id),
                    'serial_number': card.serial_number,
                    'tier_type': card.tier,
                    'status': card.status,
                    'activated_at': card.activated_date.isoformat() if card.activated_date else None,
                    'expires_at': card.expiry_date.isoformat() if card.expiry_date else None,
                    'days_until_expiry': card.days_until_expiry,
                    'is_active': card.status == 'active',
                    'features': card.get_tier_features(card.tier),
                },
                'user_tier': user.tier,
                'tier_upgraded': old_tier != user.tier,
                'previous_tier': old_tier
            }, status=status.HTTP_200_OK)
            
        except VIPDigitalCard.DoesNotExist:
            return Response(
                {'error': _('Invalid serial number or activation code.')},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"VIP card activation failed: {str(e)}")
            return Response(
                {'error': _('Card activation failed. Please try again.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            with transaction.atomic():
                # Find card with matching serial number and activation code
                try:
                    card = VIPDigitalCard.objects.get(
                        serial_number=serial_number,
                        activation_code=activation_code
                    )
                except VIPDigitalCard.DoesNotExist:
                    # Log failed attempt
                    CardActivationHistory.objects.create(
                        card=None,
                        user=user,
                        serial_number_attempted=serial_number,
                        activation_code_attempted=activation_code,
                        status='failed_invalid_serial',
                        error_message='Card not found with provided serial number and activation code',
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    return Response(
                        {
                            'error': _('Invalid serial number or activation code.'),
                            'error_code': 'CARD_NOT_FOUND'
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Check if card is already activated
                if card.status != 'inactive':
                    CardActivationHistory.objects.create(
                        card=card,
                        user=user,
                        serial_number_attempted=serial_number,
                        activation_code_attempted=activation_code,
                        status='failed_already_activated',
                        error_message=f'Card status is {card.status}',
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    return Response(
                        {
                            'error': _('This card has already been activated or is not available for activation.'),
                            'error_code': 'CARD_ALREADY_ACTIVATED'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Activate card
                try:
                    client_ip = get_client_ip(request)
                    card.activate_card(user, client_ip)
                    
                    # Log successful activation
                    CardActivationHistory.objects.create(
                        card=card,
                        user=user,
                        serial_number_attempted=serial_number,
                        activation_code_attempted=activation_code,
                        status='success',
                        ip_address=client_ip,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    logger.info(f"VIP card activated: {card.serial_number} for user {user.email}")
                    
                    return Response({
                        'success': True,
                        'message': _('VIP card activated successfully!'),
                        'card': {
                            'id': str(card.id),
                            'serial_number': card.serial_number,
                            'tier': card.tier,
                            'status': card.status,
                            'activated_date': card.activated_date.isoformat(),
                            'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
                            'days_until_expiry': card.days_until_expiry(),
                            'card_features': card.card_features,
                            'design': {
                                'primary_color': card.primary_color,
                                'secondary_color': card.secondary_color,
                                'background_image': card.background_image,
                                'hologram_pattern': card.hologram_pattern,
                                'logo_url': card.logo_url,
                            }
                        },
                        'new_tier_level': card.tier,
                        'unlocked_features': card.get_tier_benefits(),
                        'user_tier': user.tier
                    }, status=status.HTTP_200_OK)
                    
                except ValueError as e:
                    # Log failed activation
                    CardActivationHistory.objects.create(
                        card=card,
                        user=user,
                        serial_number_attempted=serial_number,
                        activation_code_attempted=activation_code,
                        status='failed_other',
                        error_message=str(e),
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    return Response(
                        {
                            'error': str(e),
                            'error_code': 'ACTIVATION_FAILED'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
        except Exception as e:
            logger.error(f"VIP card activation failed: {str(e)}")
            return Response(
                {
                    'error': _('Activation failed. Please try again.'),
                    'error_code': 'INTERNAL_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VIPCardDetailsView(APIView):
    """Get card details by serial number (for preview before activation)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, serial_number):
        """Get card details for preview"""
        serial_number = serial_number.strip().upper()
        
        # Validate serial number format
        if not re.match(r'^(VIP|VIPR)-\d{4}-\d{4}-\d{4}$', serial_number):
            return Response(
                {
                    'found': False,
                    'error': _('Invalid serial number format.')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            card = VIPDigitalCard.objects.get(serial_number=serial_number)
            
            # Don't reveal activation code or sensitive info in preview
            return Response({
                'found': True,
                'card': {
                    'id': str(card.id),
                    'serial_number': card.serial_number,
                    'tier': card.tier,
                    'status': card.status,
                    'issued_date': card.issued_date.isoformat(),
                    'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
                    'design': {
                        'primary_color': card.primary_color,
                        'secondary_color': card.secondary_color,
                        'background_image': card.background_image,
                        'hologram_pattern': card.hologram_pattern,
                        'logo_url': card.logo_url,
                    },
                    'benefits': card.get_tier_benefits()
                }
            }, status=status.HTTP_200_OK)
            
        except VIPDigitalCard.DoesNotExist:
            return Response({
                'found': False,
                'error': _('Card not found.')
            }, status=status.HTTP_404_NOT_FOUND)


class UserVIPCardsView(APIView):
    """Get user's VIP cards"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all VIP cards for authenticated user"""
        user = request.user
        
        cards = VIPDigitalCard.objects.filter(activated_by=user).order_by('-activated_date')
        
        cards_data = []
        for card in cards:
            card_data = {
                'id': str(card.id),
                'serial_number': card.serial_number,
                'tier': card.tier,
                'status': card.status,
                'issued_date': card.issued_date.isoformat(),
                'activated_date': card.activated_date.isoformat() if card.activated_date else None,
                'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
                'days_until_expiry': card.days_until_expiry(),
                'is_active': card.is_active(),
                'card_features': card.card_features,
                'design': {
                    'primary_color': card.primary_color,
                    'secondary_color': card.secondary_color,
                    'background_image': card.background_image,
                    'hologram_pattern': card.hologram_pattern,
                    'logo_url': card.logo_url,
                },
                'benefits': card.get_tier_benefits()
            }
            cards_data.append(card_data)
        
        # Get active card
        active_card = cards.filter(status='active').first()
        active_card_data = None
        if active_card and active_card.is_active():
            active_card_data = {
                'id': str(active_card.id),
                'serial_number': active_card.serial_number,
                'tier': active_card.tier,
                'expiry_date': active_card.expiry_date.isoformat() if active_card.expiry_date else None,
                'days_until_expiry': active_card.days_until_expiry(),
            }
        
        return Response({
            'cards': cards_data,
            'active_card': active_card_data,
            'user_tier': user.tier,
            'total_cards': cards.count(),
            'active_cards_count': cards.filter(status='active').count()
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_tier_level(request):
    """Get user's current tier level"""
    user = request.user
    
    # Check for active VIP card
    active_card = VIPDigitalCard.objects.filter(
        activated_by=user,
        status='active'
    ).order_by(
        # Order by tier priority (VIP Premium first)
        timezone.models.Case(
            timezone.models.When(tier='vip_premium', then=1),
            timezone.models.When(tier='vip', then=2),
            default=3
        )
    ).first()
    
    if active_card and active_card.is_active():
        return Response({
            'tier_level': active_card.tier,
            'has_vip_card': True,
            'active_card': {
                'id': str(active_card.id),
                'serial_number': active_card.serial_number,
                'tier': active_card.tier,
                'expiry_date': active_card.expiry_date.isoformat() if active_card.expiry_date else None,
                'days_until_expiry': active_card.days_until_expiry(),
            }
        })
    else:
        return Response({
            'tier_level': user.tier or 'regular',
            'has_vip_card': False,
            'active_card': None
        })


# Admin/Management Views (for generating cards)
class VIPCardGenerationView(APIView):
    """Generate VIP cards in batches (Admin only)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Generate a batch of VIP cards"""
        # Check if user is admin/staff
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': _('Permission denied. Admin access required.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tier = request.data.get('tier', 'vip')
        quantity = request.data.get('quantity', 1)
        purpose = request.data.get('purpose', 'Manual generation')
        
        if tier not in ['vip', 'vip_premium']:
            return Response(
                {'error': _('Invalid tier. Must be "vip" or "vip_premium".')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(quantity, int) or quantity < 1 or quantity > 100:
            return Response(
                {'error': _('Quantity must be between 1 and 100.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .vip_card_models import CardBatchGeneration
            
            # Create batch record
            batch = CardBatchGeneration.objects.create(
                tier=tier,
                quantity=quantity,
                generated_by=request.user,
                purpose=purpose
            )
            
            # Generate cards
            generated_cards = []
            for _ in range(quantity):
                card = VIPDigitalCard.create_card(tier)
                generated_cards.append({
                    'id': str(card.id),
                    'serial_number': card.serial_number,
                    'activation_code': card.activation_code,
                    'tier': card.tier,
                    'status': card.status,
                    'issued_date': card.issued_date.isoformat(),
                })
            
            logger.info(f"Generated {quantity} {tier} cards in batch {batch.id} by {request.user.email}")
            
            return Response({
                'message': _('Cards generated successfully!'),
                'batch_id': str(batch.id),
                'cards': generated_cards,
                'summary': {
                    'tier': tier,
                    'quantity': quantity,
                    'generated_by': request.user.email,
                    'generated_at': batch.generated_at.isoformat(),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Card generation failed: {str(e)}")
            return Response(
                {'error': _('Failed to generate cards. Please try again.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def card_activation_history(request):
    """Get card activation history for current user"""
    user = request.user
    
    history = CardActivationHistory.objects.filter(user=user).order_by('-attempt_time')[:20]
    
    history_data = []
    for record in history:
        history_data.append({
            'id': str(record.id),
            'serial_number_attempted': record.serial_number_attempted,
            'status': record.status,
            'error_message': record.error_message,
            'attempt_time': record.attempt_time.isoformat(),
            'card_activated': str(record.card.id) if record.card else None,
        })
    
    return Response({
        'history': history_data,
        'total_attempts': history.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tier_benefits(request):
    """Get benefits for all tiers"""
    benefits = {
        'vip': VIPDigitalCard.get_tier_features('vip'),
        'vip_premium': VIPDigitalCard.get_tier_features('vip_premium'),
        'tier_descriptions': {
            'vip': 'Priority booking, luxury vehicles, and VIP support',
            'vip_premium': 'Ultimate luxury with hotel partnerships, encrypted tracking, and exclusive concierge services'
        }
    }
    
    return Response(benefits)