"""
Notifications URL configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(
    r'notifications',
    views.NotificationViewSet,
    basename='notification'
)
router.register(
    r'preferences',
    views.NotificationPreferenceViewSet,
    basename='notificationpreference'
)
router.register(
    r'templates',
    views.NotificationTemplateViewSet,
    basename='notificationtemplate'
)

app_name = 'notifications'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('send/', views.send_notification, name='send_notification'),
    path('send-bulk/', views.send_bulk_notification, name='send_bulk'),
    path('delivery-status/', views.delivery_status, name='delivery_status'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
]
