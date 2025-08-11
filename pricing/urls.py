"""
VIP Ride-Hailing Platform - Pricing URLs
URL configuration for pricing API endpoints
"""

from django.urls import path
from . import views

app_name = 'pricing'

urlpatterns = [
    # Public pricing endpoints
    path('quote/', views.get_price_quote, name='price_quote'),
    path('surge-levels/', views.get_surge_levels, name='surge_levels'),
    path('zones/', views.get_pricing_zones, name='pricing_zones'),
    path('transparency/', views.get_price_transparency, name='price_transparency'),
    
    # User-specific endpoints
    path('validate-promo/', views.validate_promo_code, name='validate_promo'),
    
    # Admin/Management endpoints
    path(
        'admin/zones/<str:zone_id>/update-surge/',
        views.update_zone_surge,
        name='update_zone_surge'
    ),
    path(
        'admin/update-all-surge/',
        views.update_all_surge,
        name='update_all_surge'
    ),
]
