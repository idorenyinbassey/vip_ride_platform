"""
Notifications serializers
"""

from rest_framework import serializers
from .models import Notification, NotificationPreference, NotificationTemplate


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Notification preference serializer"""
    
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Notification template serializer"""
    
    class Meta:
        model = NotificationTemplate
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class DeliveryLogSerializer(serializers.Serializer):
    """Delivery log serializer - placeholder"""
    id = serializers.UUIDField(read_only=True)
    status = serializers.CharField()
    attempted_at = serializers.DateTimeField()


class SendNotificationSerializer(serializers.Serializer):
    """Send notification serializer"""
    recipient_id = serializers.UUIDField()
    template_id = serializers.UUIDField(required=False)
    message = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    notification_type = serializers.CharField(default='GENERAL')
    notification_data = serializers.DictField(default=dict)
    
    def validate(self, attrs):
        """Ensure at least one of template_id or message is provided"""
        if not attrs.get('template_id') and not attrs.get('message'):
            raise serializers.ValidationError(
                "Either template_id or message must be provided"
            )
        return attrs


class BulkNotificationSerializer(serializers.Serializer):
    """Bulk notification serializer"""
    recipient_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    template_id = serializers.UUIDField(required=False)
    message = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    notification_type = serializers.CharField(default='GENERAL')
    notification_data = serializers.DictField(default=dict)
    
    def validate(self, attrs):
        """Ensure at least one of template_id or message is provided"""
        if not attrs.get('template_id') and not attrs.get('message'):
            raise serializers.ValidationError(
                "Either template_id or message must be provided"
            )
        return attrs
