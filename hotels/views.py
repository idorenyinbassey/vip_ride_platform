"""
Hotels API views - Customer-facing hotel services
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Avg, Count
from django.utils import timezone
from decimal import Decimal
import logging
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# Import from hotel_partnerships since hotels module uses the same models
from hotel_partnerships.models import (
    Hotel, HotelBooking, HotelRoom
)
from hotel_partnerships.serializers import (
    HotelSerializer, HotelBookingSerializer, HotelRoomSerializer
)

logger = logging.getLogger(__name__)


class HotelReview:
    """Placeholder for hotel review model - to be implemented"""
    pass


class HotelReviewViewSet(viewsets.ModelViewSet):
    """Hotel review management ViewSet - placeholder"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Placeholder queryset"""
        return []
    
    def list(self, request):
        """Placeholder list method"""
        return Response({
            'reviews': [],
            'message': 'Hotel reviews feature coming soon'
        })


class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """Customer-facing hotel ViewSet"""
    
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get active hotels for customers"""
        return Hotel.objects.filter(
            is_active=True,
            is_partner=True
        ).annotate(
            average_rating=Avg('bookings__rating'),
            total_bookings=Count('bookings')
        )
    
    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """Get available rooms for a hotel"""
        hotel = self.get_object()
        
        try:
            # Get available rooms
            rooms = HotelRoom.objects.filter(
                hotel=hotel,
                is_active=True
            )
            
            # Filter by availability if dates provided
            check_in = request.GET.get('check_in')
            check_out = request.GET.get('check_out')
            
            if check_in and check_out:
                try:
                    # Convert string parameters to date objects
                    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
                    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
                    
                    # Check for conflicting bookings
                    conflicting_bookings = HotelBooking.objects.filter(
                        hotel=hotel,
                        status__in=['CONFIRMED', 'CHECKED_IN'],
                        check_in_date__lt=check_out_date,
                        check_out_date__gt=check_in_date
                    )
                    
                    booked_rooms = conflicting_bookings.values_list(
                        'room_number', flat=True
                    )
                    
                    rooms = rooms.exclude(room_number__in=booked_rooms)
                except ValueError:
                    return Response(
                        {'error': 'Invalid date format. Use YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = HotelRoomSerializer(rooms, many=True)
            
            return Response({
                'hotel_id': str(hotel.id),
                'available_rooms': serializer.data,
                'count': rooms.count()
            })
            
        except Exception as e:
            logger.error(f"Error getting hotel rooms: {str(e)}")
            return Response(
                {'error': 'Failed to get hotel rooms'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def amenities(self, request, pk=None):
        """Get hotel amenities"""
        hotel = self.get_object()
        
        # Mock amenities data - extend as needed
        amenities = {
            'general': [
                'Free WiFi',
                'Swimming Pool',
                'Fitness Center',
                'Restaurant',
                'Room Service'
            ],
            'business': [
                'Business Center',
                'Meeting Rooms',
                'Conference Facilities'
            ],
            'recreation': [
                'Spa',
                'Bar/Lounge',
                'Entertainment'
            ]
        }
        
        return Response({
            'hotel_id': str(hotel.id),
            'amenities': amenities
        })


class HotelBookingViewSet(viewsets.ModelViewSet):
    """Customer hotel booking ViewSet"""
    
    serializer_class = HotelBookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get bookings for current user"""
        return HotelBooking.objects.filter(
            customer=self.request.user
        ).select_related('hotel').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create booking for current user"""
        serializer.save(customer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel hotel booking"""
        booking = self.get_object()
        
        if booking.customer != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            cancellation_reason = request.data.get(
                'reason', 
                'Cancelled by customer'
            )
            
            booking.status = 'CANCELLED'
            booking.cancelled_at = timezone.now()
            booking.cancellation_reason = cancellation_reason
            booking.save()
            
            return Response({
                'status': 'cancelled',
                'booking_id': str(booking.id),
                'cancelled_at': booking.cancelled_at
            })
            
        except Exception as e:
            logger.error(f"Error cancelling booking: {str(e)}")
            return Response(
                {'error': 'Failed to cancel booking'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate hotel booking"""
        booking = self.get_object()
        
        if booking.customer != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            rating = request.data.get('rating')
            review_text = request.data.get('review', '')
            
            if not rating or not (1 <= int(rating) <= 5):
                return Response(
                    {'error': 'Rating must be between 1 and 5'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cast rating to int after validation and assign the integer value
            rating_int = int(rating)
            booking.rating = rating_int
            booking.review = review_text
            booking.rated_at = timezone.now()
            booking.save()
            
            return Response({
                'status': 'rated',
                'booking_id': str(booking.id),
                'rating': rating,
                'rated_at': booking.rated_at
            })
            
        except Exception as e:
            logger.error(f"Error rating booking: {str(e)}")
            return Response(
                {'error': 'Failed to rate booking'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_hotels(request):
    """Search hotels by various criteria"""
    try:
        # Get search parameters
        location = request.GET.get('location', '')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = int(request.GET.get('guests', 1))
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        # Base queryset
        hotels = Hotel.objects.filter(
            is_active=True,
            is_partner=True
        )
        
        # Location filter
        if location:
            hotels = hotels.filter(
                Q(name__icontains=location) |
                Q(address__icontains=location) |
                Q(city__icontains=location)
            )
        
        # Capacity filter
        if guests > 1:
            hotels = hotels.filter(
                rooms__max_occupancy__gte=guests
            ).distinct()
        
        # Price filter (if min/max price provided)
        if min_price:
            hotels = hotels.filter(rooms__price_per_night__gte=min_price)
        if max_price:
            hotels = hotels.filter(rooms__price_per_night__lte=max_price)
        
        # Availability filter
        if check_in and check_out:
            # Exclude hotels with conflicting bookings
            conflicting_hotels = HotelBooking.objects.filter(
                status__in=['CONFIRMED', 'CHECKED_IN'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            ).values_list('hotel', flat=True)
            
            hotels = hotels.exclude(id__in=conflicting_hotels)
        
        # Annotate with ratings and booking count
        hotels = hotels.annotate(
            average_rating=Avg('bookings__rating'),
            total_bookings=Count('bookings')
        )
        
        serializer = HotelSerializer(hotels[:20], many=True)  # Limit to 20 results
        
        return Response({
            'hotels': serializer.data,
            'total_count': hotels.count(),
            'search_params': {
                'location': location,
                'check_in': check_in,
                'check_out': check_out,
                'guests': guests
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching hotels: {str(e)}")
        return Response(
            {'error': 'Hotel search failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_availability(request):
    """Check hotel availability for specific dates"""
    try:
        hotel_id = request.GET.get('hotel_id')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        
        if not all([hotel_id, check_in, check_out]):
            return Response(
                {'error': 'hotel_id, check_in, and check_out are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get hotel
        try:
            hotel = Hotel.objects.get(id=hotel_id, is_active=True)
        except Hotel.DoesNotExist:
            return Response(
                {'error': 'Hotel not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all rooms
        all_rooms = HotelRoom.objects.filter(
            hotel=hotel,
            is_active=True
        )
        
        # Get conflicting bookings
        conflicting_bookings = HotelBooking.objects.filter(
            hotel=hotel,
            status__in=['CONFIRMED', 'CHECKED_IN'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        )
        
        booked_rooms = conflicting_bookings.values_list(
            'room_number', flat=True
        )
        
        available_rooms = all_rooms.exclude(room_number__in=booked_rooms)
        
        return Response({
            'hotel_id': hotel_id,
            'check_in': check_in,
            'check_out': check_out,
            'total_rooms': all_rooms.count(),
            'available_rooms': available_rooms.count(),
            'rooms': HotelRoomSerializer(available_rooms, many=True).data
        })
        
    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}")
        return Response(
            {'error': 'Failed to check availability'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def popular_hotels(request):
    """Get popular hotels based on bookings and ratings"""
    try:
        popular_hotels = Hotel.objects.filter(
            is_active=True,
            is_partner=True
        ).annotate(
            average_rating=Avg('bookings__rating'),
            total_bookings=Count('bookings')
        ).filter(
            total_bookings__gt=0
        ).order_by('-total_bookings', '-average_rating')[:10]
        
        serializer = HotelSerializer(popular_hotels, many=True)
        
        return Response({
            'popular_hotels': serializer.data,
            'criteria': 'Based on booking volume and ratings'
        })
        
    except Exception as e:
        logger.error(f"Error getting popular hotels: {str(e)}")
        return Response(
            {'error': 'Failed to get popular hotels'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nearby_hotels(request):
    """Get hotels near a location"""
    try:
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        radius = float(request.GET.get('radius', 10))  # km
        
        if not latitude or not longitude:
            return Response(
                {'error': 'latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        latitude = float(latitude)
        longitude = float(longitude)
        
        # Get all hotels (in production, use proper geospatial queries)
        hotels = Hotel.objects.filter(
            is_active=True,
            is_partner=True
        )
        
        # Filter by distance (simplified calculation)
        nearby_hotels = []
        for hotel in hotels:
            # Mock hotel coordinates (in production, store actual coordinates)
            hotel_lat = 6.5244 + (hash(hotel.name) % 100) / 1000  # Mock latitude
            hotel_lng = 3.3792 + (hash(hotel.address) % 100) / 1000  # Mock longitude
            
            distance = _calculate_distance(
                latitude, longitude, hotel_lat, hotel_lng
            )
            
            if distance <= radius:
                hotel_data = HotelSerializer(hotel).data
                hotel_data['distance_km'] = round(distance, 2)
                nearby_hotels.append(hotel_data)
        
        # Sort by distance
        nearby_hotels.sort(key=lambda x: x['distance_km'])
        
        return Response({
            'nearby_hotels': nearby_hotels[:20],  # Limit to 20 results
            'search_center': {
                'latitude': latitude,
                'longitude': longitude
            },
            'radius_km': radius
        })
        
    except Exception as e:
        logger.error(f"Error getting nearby hotels: {str(e)}")
        return Response(
            {'error': 'Failed to get nearby hotels'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hotel_amenities(request):
    """Get available hotel amenities"""
    try:
        amenities_list = [
            {'category': 'Internet', 'items': ['Free WiFi', 'Business Center']},
            {'category': 'Fitness', 'items': ['Gym', 'Swimming Pool', 'Spa']},
            {'category': 'Food & Dining', 'items': ['Restaurant', 'Room Service', 'Bar']},
            {'category': 'Services', 'items': ['Concierge', 'Laundry', 'Parking']},
            {'category': 'Entertainment', 'items': ['TV', 'Cable/Satellite', 'Game Room']},
        ]
        
        return Response({'amenities': amenities_list})
        
    except Exception as e:
        logger.error(f"Error getting amenities: {str(e)}")
        return Response(
            {'error': 'Failed to get amenities'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r
