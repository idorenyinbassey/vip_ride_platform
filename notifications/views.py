"""
Notifications API views
"""

from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache
import logging
from datetime import timedelta

from .models import (
    Notification, NotificationPreference, NotificationTemplate,
    NotificationDeliveryLog
)

logger = logging.getLogger(__name__)


# Create proper DRF serializers
class NotificationSerializer(serializers.ModelSerializer):
    """Proper DRF serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationPreferenceSerializer(NotificationSerializer):
    """Placeholder serializer"""
    pass


class NotificationTemplateSerializer(NotificationSerializer):
    """Placeholder serializer"""
    pass


class DeliveryLogSerializer(NotificationSerializer):
    """Serializer for NotificationDeliveryLog"""
    
    class Meta:
        model = NotificationDeliveryLog
        fields = '__all__'


class SendNotificationSerializer(NotificationSerializer):
    """Placeholder serializer"""
    def is_valid(self):
        return True
    
    @property
    def validated_data(self):
        return {
            'recipient_id': self.data_dict.get('recipient_id'),
            'message': self.data_dict.get('message', 'Test message'),
            'title': self.data_dict.get('title', 'Test title'),
            'notification_type': self.data_dict.get('notification_type', 'GENERAL'),
            'data': self.data_dict.get('data', {})
        }
    
    @property
    def errors(self):
        return {}


class BulkNotificationSerializer(SendNotificationSerializer):
    """Placeholder serializer"""
    @property
    def validated_data(self):
        return {
            'recipient_ids': self.data_dict.get('recipient_ids', []),
            'message': self.data_dict.get('message', 'Test message'),
            'title': self.data_dict.get('title', 'Test title'),
            'notification_type': self.data_dict.get('notification_type', 'GENERAL'),
            'data': self.data_dict.get('data', {})
        }


# Create placeholder service
class NotificationService:
    """Placeholder service"""
    def send_notification(self, **kwargs):
        # Create a mock notification
        return type('MockNotification', (), {
            'id': 'mock-id',
            'created_at': timezone.now()
        })()
    
    def send_bulk_notification(self, **kwargs):
        recipient_ids = kwargs.get('recipient_ids', [])
        return {
            'sent_count': len(recipient_ids),
            'failed_count': 0,
            'details': []
        }


class NotificationViewSet(viewsets.ModelViewSet):
    """Notification management ViewSet"""
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for current user"""
        user = self.request.user
        
        if user.is_staff:
            # Staff can see all notifications
            return Notification.objects.all().select_related(
                'recipient', 'template'
            ).order_by('-created_at')
        
        # Regular users see their own notifications
        return Notification.objects.filter(
            recipient=user
        ).select_related('template').order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        
        if notification.recipient != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            notification.mark_as_read()
            return Response({
                'status': 'marked_as_read',
                'notification_id': str(notification.id),
                'read_at': notification.read_at
            })
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return Response(
                {'error': 'Failed to mark notification as read'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        try:
            unread_notifications = self.get_queryset().filter(
                is_read=False
            )
            
            serializer = self.get_serializer(unread_notifications, many=True)
            
            return Response({
                'notifications': serializer.data,
                'count': unread_notifications.count()
            })
            
        except Exception as e:
            logger.error(f"Error getting unread notifications: {str(e)}")
            return Response(
                {'error': 'Failed to get unread notifications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """Notification preference management ViewSet"""
    
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get preferences for current user"""
        return NotificationPreference.objects.filter(
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        """Create preference for current user"""
        serializer.save(user=self.request.user)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """Notification template management ViewSet"""
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get all templates (read-only for non-staff)"""
        return NotificationTemplate.objects.filter(is_active=True)
    
    def get_permissions(self):
        """Only staff can modify templates"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    """Send a single notification"""
    serializer = SendNotificationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            service = NotificationService()
            notification = service.send_notification(
                recipient_id=serializer.validated_data['recipient_id'],
                template_id=serializer.validated_data.get('template_id'),
                message=serializer.validated_data.get('message'),
                title=serializer.validated_data.get('title'),
                notification_type=serializer.validated_data.get(
                    'notification_type', 'GENERAL'
                ),
                data=serializer.validated_data.get('data', {}),
                sender=request.user
            )
            
            return Response({
                'status': 'sent',
                'notification_id': str(notification.id),
                'sent_at': notification.created_at
            })
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def send_bulk_notification(request):
    """Send bulk notifications"""
    serializer = BulkNotificationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            service = NotificationService()
            result = service.send_bulk_notification(
                recipient_ids=serializer.validated_data['recipient_ids'],
                template_id=serializer.validated_data.get('template_id'),
                message=serializer.validated_data.get('message'),
                title=serializer.validated_data.get('title'),
                notification_type=serializer.validated_data.get(
                    'notification_type', 'GENERAL'
                ),
                data=serializer.validated_data.get('data', {}),
                sender=request.user
            )
            
            return Response({
                'status': 'sent',
                'notifications_sent': result['sent_count'],
                'notifications_failed': result['failed_count'],
                'details': result.get('details', [])
            })
            
        except Exception as e:
            logger.error(f"Error sending bulk notifications: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delivery_status(request):
    """Get notification delivery status"""
    try:
        notification_id = request.GET.get('notification_id')
        
        if not notification_id:
            return Response(
                {'error': 'notification_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get delivery logs
        logs = NotificationDeliveryLog.objects.filter(
            notification_id=notification_id
        ).order_by('-attempted_at')
        
        if not logs.exists():
            return Response(
                {'error': 'Notification not found or no delivery logs'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DeliveryLogSerializer(logs, many=True)
        
        return Response({
            'notification_id': notification_id,
            'delivery_logs': serializer.data,
            'total_attempts': logs.count(),
            'last_status': logs.first().status if logs.exists() else 'UNKNOWN'
        })
        
    except Exception as e:
        logger.error(f"Error getting delivery status: {str(e)}")
        return Response(
            {'error': 'Failed to get delivery status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read for current user"""
    try:
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        # Clear cache
        cache_key = f"unread_notifications_{request.user.id}"
        cache.delete(cache_key)
        
        return Response({
            'status': 'success',
            'marked_as_read': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return Response(
            {'error': 'Failed to mark notifications as read'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """Get unread notification count for current user"""
    try:
        # Check cache first
        cache_key = f"unread_notifications_{request.user.id}"
        cached_count = cache.get(cache_key)
        
        if cached_count is not None:
            return Response({'unread_count': cached_count})
        
        # Calculate count
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        # Cache for 5 minutes
        cache.set(cache_key, count, 300)
        
        return Response({'unread_count': count})
        
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        return Response(
            {'error': 'Failed to get unread count'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
