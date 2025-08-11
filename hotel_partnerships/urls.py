from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'hotels', views.HotelViewSet)
router.register(r'staff', views.HotelStaffViewSet)
router.register(r'rooms', views.HotelRoomViewSet)
router.register(r'guests', views.HotelGuestViewSet)
router.register(r'bookings', views.HotelBookingViewSet)
router.register(r'bulk-events', views.BulkBookingEventViewSet)
router.register(r'commission-reports', views.HotelCommissionReportViewSet)
router.register(r'pms-logs', views.PMSIntegrationLogViewSet)

app_name = 'hotel_partnerships'

urlpatterns = [
    path('api/', include(router.urls)),
]
