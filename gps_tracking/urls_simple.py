from django.urls import path
from . import views

app_name = 'gps_tracking'

# Simplified URL patterns for testing migrations
urlpatterns = [
    # GPS Locations
    path('locations/', 
         views.GPSLocationListCreateView.as_view(), 
         name='gps-location-list'),
    path('locations/<uuid:pk>/', 
         views.GPSLocationDetailView.as_view(), 
         name='gps-location-detail'),
    
    # Route Optimization  
    path('routes/<uuid:pk>/', 
         views.RouteOptimizationDetailView.as_view(), 
         name='route-optimization-detail'),
]
