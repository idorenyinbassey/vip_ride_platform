from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    # Client dashboard
    path('client/profile/', views.client_profile, name='client_profile'),
    path('client/book/', views.client_book_ride, name='client_book_ride'),
    path(
        'client/rides/',
        views.client_ride_history,
        name='client_ride_history'
    ),
    path('client/payments/', views.client_payments, name='client_payments'),
    path('client/vip/', views.client_vip_features, name='client_vip_features'),
    path(
        'client/premium/',
        views.client_premium_features,
        name='client_premium_features'
    ),
    path('client/wallet/', views.client_wallet, name='client_wallet'),
    path('client/support/', views.client_support, name='client_support'),
    # Driver dashboard
    path(
        'driver/onboarding/',
        views.driver_onboarding,
        name='driver_onboarding'
    ),
    path('driver/documents/', views.driver_documents, name='driver_documents'),
    path('driver/earnings/', views.driver_earnings, name='driver_earnings'),
    path('driver/vehicles/', views.driver_vehicles, name='driver_vehicles'),
    path(
        'driver/subscription/',
        views.driver_subscription,
        name='driver_subscription'
    ),
    path(
        'driver/performance/',
        views.driver_performance,
        name='driver_performance'
    ),
    path(
        'driver/fleet/',
        views.driver_fleet_integration,
        name='driver_fleet_integration'
    ),
    # Portal logout (session-based)
    path('logout/', views.logout_view, name='logout'),
]
