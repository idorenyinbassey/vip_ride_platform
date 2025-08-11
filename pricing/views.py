"""
VIP Ride-Hailing Platform - Pricing API Views
RESTful endpoints for price quotes and transparency
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import logging

from .engines import PricingEngine, SurgeManagementService
from .models import PricingZone, PromotionalCode
from .serializers import (
    PriceQuoteRequestSerializer, PriceQuoteResponseSerializer,
    SurgeLevelSerializer, PricingZoneSerializer
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_price_quote(request):
    """
    Get price quote for a ride with all pricing factors
    
    POST /api/pricing/quote/
    {
        "pickup_lat": 6.5244,
        "pickup_lng": 3.3792,
        "dropoff_lat": 6.4474,
        "dropoff_lng": 3.3903,
        "distance_km": "15.2",
        "estimated_duration_minutes": 25,
        "vehicle_type": "economy",
        "promo_code": "SAVE20"
    }
    """
    serializer = PriceQuoteRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid request data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    
    try:
        # Create coordinates from request data
        pickup_lat = Decimal(str(data['pickup_lat']))
        pickup_lng = Decimal(str(data['pickup_lng']))
        dropoff_lat = Decimal(str(data['dropoff_lat']))
        dropoff_lng = Decimal(str(data['dropoff_lng']))
        
        # Initialize pricing engine
        engine = PricingEngine()
        
        # Calculate price
        pricing_result = engine.calculate_ride_price(
            user=request.user,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            dropoff_lat=dropoff_lat,
            dropoff_lng=dropoff_lng,
            distance_km=data['distance_km'],
            estimated_duration_minutes=data['estimated_duration_minutes'],
            vehicle_type=data['vehicle_type'],
            promo_code=data.get('promo_code')
        )
        
        # Format response
        response_serializer = PriceQuoteResponseSerializer(pricing_result)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except ValueError as e:
        logger.warning(f"Price calculation error for user {request.user.id}: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Unexpected error in price calculation: {e}")
        return Response(
            {'error': 'Unable to calculate price at this time'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_surge_levels(request):
    """
    Get current surge levels for all zones
    
    GET /api/pricing/surge-levels/
    """
    try:
        surge_data = SurgeManagementService.get_current_surge_levels()
        
        # Format for response
        formatted_data = []
        for zone_name, surge_info in surge_data.items():
            formatted_data.append({
                'zone_name': zone_name,
                'surge_level': surge_info['level'],
                'multiplier': surge_info['multiplier'],
                'demand_ratio': surge_info['demand_ratio']
            })
        
        serializer = SurgeLevelSerializer(formatted_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting surge levels: {e}")
        return Response(
            {'error': 'Unable to retrieve surge levels'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_pricing_zones(request):
    """
    Get all active pricing zones with basic info
    
    GET /api/pricing/zones/
    """
    try:
        zones = PricingZone.objects.filter(is_active=True)
        serializer = PricingZoneSerializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting pricing zones: {e}")
        return Response(
            {'error': 'Unable to retrieve pricing zones'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_promo_code(request):
    """
    Validate promotional code for user
    
    POST /api/pricing/validate-promo/
    {
        "promo_code": "SAVE20"
    }
    """
    promo_code = request.data.get('promo_code', '').strip().upper()
    if not promo_code:
        return Response(
            {'error': 'Promo code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        promo = PromotionalCode.objects.get(code=promo_code)
        can_use, reason = promo.can_user_use(request.user)
        
        if can_use:
            return Response({
                'valid': True,
                'code': promo.code,
                'description': promo.description,
                'discount_type': promo.discount_type,
                'discount_value': str(promo.discount_value),
                'applies_to_surge': promo.applies_to_surge
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'valid': False,
                'reason': reason
            }, status=status.HTTP_200_OK)
            
    except PromotionalCode.DoesNotExist:
        return Response({
            'valid': False,
            'reason': 'Invalid promo code'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error validating promo code {promo_code}: {e}")
        return Response(
            {'error': 'Unable to validate promo code'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_price_transparency(request):
    """
    Get detailed price transparency info for a location
    
    GET /api/pricing/transparency/?lat=6.5244&lng=3.3792
    """
    try:
        lat = Decimal(str(request.GET.get('lat', 0)))
        lng = Decimal(str(request.GET.get('lng', 0)))
        
        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get zone info
        zones = PricingZone.objects.filter(is_active=True)
        zone = None
        for z in zones:
            if z.contains_point(lat, lng):
                zone = z
                break
        
        # Get current surge and event multipliers
        engine = PricingEngine()
        surge_multiplier = engine.get_surge_multiplier(lat, lng, timezone.now())
        event_multiplier = engine.get_event_multiplier(lat, lng, timezone.now())
        
        transparency_info = engine._generate_transparency_info(
            zone, surge_multiplier, event_multiplier, {}
        )
        
        return Response({
            'location': {'lat': float(lat), 'lng': float(lng)},
            'zone': zone.name if zone else 'Default Zone',
            'transparency_info': transparency_info
        }, status=status.HTTP_200_OK)
        
    except ValueError:
        return Response(
            {'error': 'Invalid coordinates'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting price transparency: {e}")
        return Response(
            {'error': 'Unable to retrieve transparency info'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Admin/Management Views (require staff permissions)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_zone_surge(request, zone_id):
    """
    Manually update surge pricing for a zone (staff only)
    
    POST /api/pricing/admin/zones/{zone_id}/update-surge/
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Staff access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        SurgeManagementService.update_zone_surge(zone_id)
        return Response(
            {'message': f'Surge updated for zone {zone_id}'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error updating surge for zone {zone_id}: {e}")
        return Response(
            {'error': 'Unable to update surge'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_all_surge(request):
    """
    Update surge pricing for all zones (staff only)
    
    POST /api/pricing/admin/update-all-surge/
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Staff access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        SurgeManagementService.update_all_zones_surge()
        return Response(
            {'message': 'Surge updated for all zones'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error updating surge for all zones: {e}")
        return Response(
            {'error': 'Unable to update surge'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
