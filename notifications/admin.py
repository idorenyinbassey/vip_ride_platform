"""
Django Admin Configuration for Notifications App
"""

from django.contrib import admin
from .models import (
    Notification, NotificationTemplate,
    NotificationDeliveryLog, NotificationPreference
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notifications"""
    
    list_display = [
        'recipient', 'notification_type', 'title', 'status', 'created_at'
    ]
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['recipient__email', 'title', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin for Notification Templates"""
    
    list_display = [
        'id', 'notification_type', 'is_active', 'created_at'
    ]
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['content']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(NotificationDeliveryLog)
class NotificationDeliveryLogAdmin(admin.ModelAdmin):
    """Admin for Notification Delivery Logs"""
    
    list_display = ['notification', 'delivery_status', 'created_at']
    list_filter = ['delivery_status', 'created_at']
    search_fields = ['notification__id']
    readonly_fields = ['id', 'notification', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin for Notification Preferences"""
    
    list_display = [
        'user', 'created_at'
    ]
    list_filter = [
        'created_at'
    ]
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
