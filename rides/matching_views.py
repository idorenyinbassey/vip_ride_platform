# API Views for Ride Matching System
"""
API endpoints for ride matching functionality
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging

from accounts.models import Driver, UserTier
from accounts.permissions import IsVIPUser, IsConciergeUser, IsAdminUser
from .models import Ride, RideStatus, RideOffer
from .models import SurgeZone, RideMatchingLog
from .matching import RideMatchingController
from .matching_serializers import (
    RideSerializer, RideOfferSerializer, SurgeZoneSerializer,
    RideMatchingLogSerializer
)

logger = logging.getLogger(__name__)


class RideMatchingViewSet(viewsets.ViewSet):
    """API endpoints for ride matching operations"""
    
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Dynamic permissions based on action"""
        if self.action in ['surge_zones', 'matching_stats']:
            permission_classes = [IsAdminUser]
        elif self.action in ['driver_response', 'driver_status']:
            permission_classes = [IsConciergeUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'])
    def request_ride(self, request):
        """
        Request a new ride and trigger matching algorithm
        
        POST /api/rides/matching/request_ride/
        """
        try:
            # Validate ride request data
            serializer = RideSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create ride instance
            ride_data = serializer.validated_data
            ride_data['customer'] = request.user
            ride_data['customer_tier'] = request.user.profile.tier
            ride_data['status'] = RideStatus.PENDING
            ride_data['requested_at'] = timezone.now()
            
            ride = Ride.objects.create(**ride_data)
            
            # Initialize matching controller
            controller = RideMatchingController()
            
            # Process ride request
            matching_result = controller.process_ride_request(ride)
            
            # Log matching attempt
            RideMatchingLog.objects.create(
                ride=ride,
                search_radius_km=20.0,  # Would be dynamic based on tier
                drivers_in_radius=matching_result.get('drivers_found', 0),
                drivers_eligible=matching_result.get('drivers_found', 0),
                drivers_contacted=matching_result.get('offers_created', 0),
                offers_created=matching_result.get('offers_created', 0),
                match_successful=matching_result.get('success', False),
                surge_multiplier=matching_result.get('surge_multiplier', 1.0),
                customer_tier=ride.customer_tier,
                ride_type=ride.ride_type
            )
            
            # Prepare response
            response_data = {
                'ride_id': str(ride.id),
                'status': 'matching_started',
                'matching_result': matching_result,
                'estimated_matching_time': '2-5 minutes'
            }
            
            if matching_result.get('success'):
                response_data['drivers'] = matching_result.get('driver_scores', [])
                response_data['surge_multiplier'] = matching_result.get('surge_multiplier')
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in ride request: {e}")
            return Response(
                {'error': 'Failed to process ride request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def driver_response(self, request):
        """
        Handle driver response to ride offer
        
        POST /api/rides/matching/driver_response/
        Body: {
            "offer_id": "uuid",
            "accepted": true/false
        }
        """
        try:
            # Validate driver
            try:
                driver = Driver.objects.get(user=request.user)
            except Driver.DoesNotExist:
                return Response(
                    {'error': 'Only drivers can respond to offers'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get offer
            offer_id = request.data.get('offer_id')
            accepted = request.data.get('accepted', False)
            
            if not offer_id:
                return Response(
                    {'error': 'offer_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                offer = RideOffer.objects.get(
                    id=offer_id,
                    driver=request.user
                )
            except RideOffer.DoesNotExist:
                return Response(
                    {'error': 'Offer not found or not assigned to you'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Process response
            controller = RideMatchingController()
            result = controller.handle_driver_response(offer, accepted)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in driver response: {e}")
            return Response(
                {'error': 'Failed to process driver response'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def active_offers(self, request):
        """
        Get active offers for the current driver
        
        GET /api/rides/matching/active_offers/
        """
        try:
            # Validate driver
            try:
                driver = Driver.objects.get(user=request.user)
            except Driver.DoesNotExist:
                return Response(
                    {'error': 'Only drivers can view offers'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get active offers
            offers = RideOffer.objects.filter(
                driver=request.user,
                status=RideOffer.OfferStatus.PENDING,
                expires_at__gt=timezone.now()
            ).select_related('ride')
            
            # Expire old offers
            for offer in offers:
                offer.expire_if_needed()
            
            # Refresh queryset after expiration
            active_offers = RideOffer.objects.filter(
                driver=request.user,
                status=RideOffer.OfferStatus.PENDING,
                expires_at__gt=timezone.now()
            ).select_related('ride')
            
            serializer = RideOfferSerializer(active_offers, many=True)
            
            return Response({
                'offers': serializer.data,
                'count': active_offers.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting active offers: {e}")
            return Response(
                {'error': 'Failed to retrieve offers'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['patch'])
    def driver_status(self, request):
        """
        Update driver availability status
        
        PATCH /api/rides/matching/driver_status/
        Body: {
            "is_available": true/false,
            "current_location": {
                "latitude": 6.5244,
                "longitude": 3.3792
            }
        }
        """
        try:
            # Validate driver
            try:
                driver = Driver.objects.get(user=request.user)
            except Driver.DoesNotExist:
                return Response(
                    {'error': 'Only drivers can update status'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update availability
            is_available = request.data.get('is_available')
            if is_available is not None:
                driver.is_available = is_available
            
            # Update location
            location = request.data.get('current_location')
            if location:
                driver.current_location_lat = Decimal(str(location['latitude']))
                driver.current_location_lng = Decimal(str(location['longitude']))
                driver.last_location_update = timezone.now()
            
            driver.save()
            
            return Response({
                'status': 'updated',
                'is_available': driver.is_available,
                'is_online': driver.is_online,
                'last_location_update': driver.last_location_update
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating driver status: {e}")
            return Response(
                {'error': 'Failed to update driver status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def surge_zones(self, request):
        """
        Get active surge zones
        
        GET /api/rides/matching/surge_zones/
        """
        try:
            active_zones = SurgeZone.objects.filter(
                is_active=True,
                active_until__gt=timezone.now()
            )
            
            serializer = SurgeZoneSerializer(active_zones, many=True)
            
            return Response({
                'surge_zones': serializer.data,
                'count': active_zones.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting surge zones: {e}")
            return Response(
                {'error': 'Failed to retrieve surge zones'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def matching_stats(self, request):
        """
        Get ride matching statistics
        
        GET /api/rides/matching/matching_stats/
        """
        try:
            controller = RideMatchingController()
            stats = controller.get_ride_matching_stats()
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting matching stats: {e}")
            return Response(
                {'error': 'Failed to retrieve statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def ride_status(self, request, pk=None):
        """
        Get detailed status of a specific ride
        
        GET /api/rides/matching/{ride_id}/ride_status/
        """
        try:
            ride = Ride.objects.get(id=pk, customer=request.user)
            
            # Get offers for this ride
            offers = RideOffer.objects.filter(ride=ride).order_by('-created_at')
            
            response_data = {
                'ride': RideSerializer(ride).data,
                'offers': RideOfferSerializer(offers, many=True).data,
                'offers_count': offers.count(),
                'pending_offers': offers.filter(
                    status=RideOffer.OfferStatus.PENDING
                ).count()
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Ride.DoesNotExist:
            return Response(
                {'error': 'Ride not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting ride status: {e}")
            return Response(
                {'error': 'Failed to retrieve ride status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def cancel_ride(self, request):
        """
        Cancel a ride request
        
        POST /api/rides/matching/cancel_ride/
        Body: {
            "ride_id": "uuid",
            "reason": "customer_request"
        }
        """
        try:
            ride_id = request.data.get('ride_id')
            reason = request.data.get('reason', 'customer_request')
            
            if not ride_id:
                return Response(
                    {'error': 'ride_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ride = Ride.objects.get(id=ride_id, customer=request.user)
            except Ride.DoesNotExist:
                return Response(
                    {'error': 'Ride not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if ride can be cancelled
            if ride.status in [RideStatus.COMPLETED, RideStatus.CANCELLED]:
                return Response(
                    {'error': 'Ride cannot be cancelled'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cancel ride and reject pending offers
            with transaction.atomic():
                ride.status = RideStatus.CANCELLED
                ride.cancelled_at = timezone.now()
                ride.cancellation_reason = reason
                ride.save()
                
                # Reject all pending offers
                RideOffer.objects.filter(
                    ride=ride,
                    status=RideOffer.OfferStatus.PENDING
                ).update(status=RideOffer.OfferStatus.REJECTED)
                
                # Update driver availability if assigned
                if ride.driver:
                    try:
                        driver = Driver.objects.get(user=ride.driver)
                        driver.is_available = True
                        driver.save()
                    except Driver.DoesNotExist:
                        pass
            
            return Response({
                'status': 'cancelled',
                'ride_id': str(ride.id),
                'cancelled_at': ride.cancelled_at
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error cancelling ride: {e}")
            return Response(
                {'error': 'Failed to cancel ride'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
