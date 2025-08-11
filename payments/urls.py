"""
Payment system URL configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(
    r'payment-methods',
    views.PaymentMethodViewSet,
    basename='paymentmethod'
)
router.register(r'currencies', views.CurrencyViewSet, basename='currency')
router.register(
    r'driver-payouts',
    views.DriverPayoutViewSet,
    basename='driverpayout'
)
router.register(
    r'disputes',
    views.PaymentDisputeViewSet,
    basename='paymentdispute'
)

app_name = 'payments'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Webhook endpoints
    path(
        'webhooks/paystack/',
        views.paystack_webhook,
        name='paystack_webhook'
    ),
    path(
        'webhooks/flutterwave/',
        views.flutterwave_webhook,
        name='flutterwave_webhook'
    ),
    path(
        'webhooks/stripe/',
        views.stripe_webhook,
        name='stripe_webhook'
    ),
    
    # Custom endpoints
    path(
        'commission-reports/',
        views.commission_reports,
        name='commission_reports'
    ),
    path(
        'payment-history/',
        views.payment_history,
        name='payment_history'
    ),
    path(
        'gateway-status/',
        views.gateway_status,
        name='gateway_status'
    ),
]
