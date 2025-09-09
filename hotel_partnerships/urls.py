from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Admin/Staff router for hotel management
admin_router = DefaultRouter()
admin_router.register(r'hotels', views.HotelViewSet)
admin_router.register(r'staff', views.HotelStaffViewSet)
admin_router.register(r'rooms', views.HotelRoomViewSet)
admin_router.register(r'guests', views.HotelGuestViewSet)
admin_router.register(r'bookings', views.HotelBookingViewSet)
admin_router.register(r'bulk-events', views.BulkBookingEventViewSet)
admin_router.register(r'commission-reports', views.HotelCommissionReportViewSet)
admin_router.register(r'pms-logs', views.PMSIntegrationLogViewSet)

# Customer router for public hotel services
customer_router = DefaultRouter()
customer_router.register(r'hotels', views.CustomerHotelViewSet, basename='customer-hotel')
customer_router.register(r'bookings', views.CustomerHotelBookingViewSet, basename='customer-booking')

app_name = 'hotel_partnerships'

urlpatterns = [
    # Customer-facing endpoints (public API)
    path('', include(customer_router.urls)),
    
    # Admin/Staff endpoints (protected)
    path('admin/', include(admin_router.urls)),
    
    # Legacy API support (redirects to admin)
    path('api/', include(admin_router.urls)),
]
