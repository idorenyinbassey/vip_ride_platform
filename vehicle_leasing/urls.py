"""
Vehicle Leasing URL configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(
    r'vehicles',
    views.VehicleListingViewSet,
    basename='vehiclelisting'
)
router.register(
    r'leases',
    views.VehicleLeaseViewSet,
    basename='vehiclelease'
)
router.register(
    r'payments',
    views.LeasePaymentViewSet,
    basename='leasepayment'
)

app_name = 'vehicle_leasing'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('search/', views.search_vehicles, name='search_vehicles'),
    path('calculate-lease/', views.calculate_lease, name='calculate_lease'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('fleet-dashboard/', views.fleet_dashboard, name='fleet_dashboard'),
]
