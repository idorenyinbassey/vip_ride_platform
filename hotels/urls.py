"""
Hotels URL configuration - Customer-facing hotel services
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(
    r'hotels',
    views.HotelViewSet,
    basename='hotel'
)
router.register(
    r'bookings',
    views.HotelBookingViewSet,
    basename='hotelbooking'
)
router.register(
    r'reviews',
    views.HotelReviewViewSet,
    basename='hotelreview'
)

app_name = 'hotels'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('search/', views.search_hotels, name='search_hotels'),
    path('availability/', views.check_availability, name='check_availability'),
    path('popular/', views.popular_hotels, name='popular_hotels'),
    path('nearby/', views.nearby_hotels, name='nearby_hotels'),
    path('amenities/', views.hotel_amenities, name='hotel_amenities'),
]
