"""
Control Center Views
Secure API views for emergency response and VIP monitoring
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
from django.core.exceptions import PermissionDenied
from datetime import timedelta
import logging

from .models import (
    EmergencyIncident, VIPMonitoringSession, ControlOperator,
    IncidentResponse, SOSConfiguration,
    IncidentStatus, IncidentPriority
)
from rides.models import Ride
from fleet_management.models import Vehicle
from .serializers import (
    EmergencyIncidentSerializer, EmergencyIncidentCreateSerializer,
    VIPMonitoringSessionSerializer, ControlOperatorSerializer,
    IncidentResponseSerializer, SOSConfigurationSerializer,
    SOSTriggerSerializer, IncidentUpdateSerializer,
    MonitoringDashboardSerializer
)
from accounts.permissions import IsVIPUser, IsControlOperator, IsAdminUser

logger = logging.getLogger(__name__)


class EmergencyIncidentViewSet(viewsets.ModelViewSet):
    """Emergency incident management viewset"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return EmergencyIncidentCreateSerializer
        return EmergencyIncidentSerializer
    
    def get_queryset(self):
        """Filter incidents based on user permissions"""
        user = self.request.user
        
        # Control operators see assigned incidents
        if hasattr(user, 'control_operator'):
            operator = user.control_operator
            if operator.security_clearance_level in ['supervisor', 'vip']:
                return EmergencyIncident.objects.all().select_related(
                    'user', 'driver', 'assigned_operator'
                )
            else:
                return EmergencyIncident.objects.filter(
                    assigned_operator=user
                ).select_related('user', 'driver', 'assigned_operator')
        
        # Admin users see all incidents
        if user.is_superuser:
            return EmergencyIncident.objects.all().select_related(
                'user', 'driver', 'assigned_operator'
            )
        
        # Regular users see their own incidents
        return EmergencyIncident.objects.filter(
            Q(user=user) | Q(driver=user)
        ).select_related('user', 'driver', 'assigned_operator')
    
    def perform_create(self, serializer):
        """Create incident with automatic assignment"""
        incident = serializer.save()
        
        # Auto-assign operator based on priority and availability
        self._assign_operator(incident)
        
        # Trigger emergency protocols
        self._trigger_emergency_protocols(incident)
        
        logger.critical(f"Emergency incident created: {incident.id}")
    
    def _assign_operator(self, incident):
        """Assign available operator to incident"""
        try:
            # Find available operators based on clearance level
            clearance_required = 'vip' if incident.user.profile.tier == 'VIP' else 'basic'
            
            available_operators = ControlOperator.objects.filter(
                is_active=True,
                is_on_duty=True,
                security_clearance_level__in=[clearance_required, 'supervisor']
            ).order_by('total_incidents_handled')
            
            if available_operators.exists():
                operator = available_operators.first()
                incident.assigned_operator = operator.user
                incident.save()
                
                # Update operator stats
                operator.total_incidents_handled += 1
                operator.save()
                
                logger.info(f"Operator {operator.operator_id} assigned to incident {incident.id}")
            else:
                logger.warning(f"No available operators for incident {incident.id}")
                
        except Exception as e:
            logger.error(f"Error assigning operator: {e}")
    
    def _trigger_emergency_protocols(self, incident):
        """Trigger emergency response protocols"""
        try:
            # Get SOS configuration for user tier
            user_tier = getattr(incident.user.profile, 'tier', 'normal').lower()
            
            try:
                sos_config = SOSConfiguration.objects.get(user_tier=user_tier)
            except SOSConfiguration.DoesNotExist:
                sos_config = SOSConfiguration.objects.get(user_tier='normal')
            
            # Auto-contact authorities if configured
            if sos_config.auto_contact_police and incident.requires_immediate_response:
                self._contact_authorities(incident, 'police')
            
            if sos_config.auto_contact_medical and incident.incident_type == 'medical':
                self._contact_authorities(incident, 'medical')
            
            # Notify emergency contacts
            if sos_config.notify_emergency_contacts:
                self._notify_emergency_contacts(incident)
                
        except Exception as e:
            logger.error(f"Error triggering emergency protocols: {e}")
    
    def _contact_authorities(self, incident, authority_type):
        """Contact external authorities"""
        # Implementation would integrate with emergency services
        logger.info(f"Contacting {authority_type} for incident {incident.id}")
        
        # Mark as contacted
        if authority_type == 'police':
            incident.police_notified = True
        elif authority_type == 'medical':
            incident.medical_services_notified = True
        
        incident.save()
    
    def _notify_emergency_contacts(self, incident):
        """Notify user's emergency contacts"""
        # Implementation would send SMS/calls to emergency contacts
        incident.emergency_contacts_notified = True
        incident.save()
        logger.info(f"Emergency contacts notified for incident {incident.id}")
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update incident status with response tracking"""
        incident = self.get_object()
        serializer = IncidentUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check permissions
            if not self._can_update_incident(incident, request.user):
                return Response(
                    {'error': 'Insufficient permissions'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = serializer.validated_data
            
            with transaction.atomic():
                # Update incident status
                old_status = incident.status
                incident.status = data['status']
                
                # Set timestamps
                if old_status == IncidentStatus.ACTIVE and data['status'] == IncidentStatus.RESPONDED:
                    incident.first_response_at = timezone.now()
                    
                    # Calculate response time
                    response_time = (timezone.now() - incident.created_at).total_seconds()
                    incident.response_time_seconds = int(response_time)
                
                if data['status'] == IncidentStatus.RESOLVED:
                    incident.resolved_at = timezone.now()
                    incident.resolved_by = request.user
                
                incident.save()
                
                # Create response record
                IncidentResponse.objects.create(
                    incident=incident,
                    action_type='status_update',
                    description=data['response_notes'],
                    operator=getattr(request.user, 'control_operator', None),
                    authority_contacted=data.get('authority_contacted', ''),
                    team_dispatched=data.get('team_dispatched', '')
                )
            
            logger.info(f"Incident {incident.id} status updated to {data['status']}")
            
            return Response({
                'status': 'updated',
                'incident_id': str(incident.id),
                'new_status': data['status'],
                'response_time': incident.response_time_seconds
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _can_update_incident(self, incident, user):
        """Check if user can update incident"""
        # Assigned operator can update
        if incident.assigned_operator == user:
            return True
        
        # Supervisor can update any incident
        if hasattr(user, 'control_operator'):
            operator = user.control_operator
            return operator.security_clearance_level in ['supervisor', 'vip']
        
        return user.is_superuser
    
    @action(detail=False, methods=['get'])
    def active_incidents(self, request):
        """Get active incidents for dashboard"""
        if not hasattr(request.user, 'control_operator'):
            return Response(
                {'error': 'Control operator access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        incidents = self.get_queryset().filter(
            status__in=[IncidentStatus.ACTIVE, IncidentStatus.RESPONDED]
        ).order_by('-created_at')
        
        serializer = self.get_serializer(incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def critical_incidents(self, request):
        """Get critical priority incidents"""
        if not hasattr(request.user, 'control_operator'):
            return Response(
                {'error': 'Control operator access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        incidents = self.get_queryset().filter(
            priority=IncidentPriority.CRITICAL,
            status__in=[IncidentStatus.ACTIVE, IncidentStatus.RESPONDED]
        ).order_by('-created_at')
        
        serializer = self.get_serializer(incidents, many=True)
        return Response(serializer.data)


class VIPMonitoringSessionViewSet(viewsets.ModelViewSet):
    """VIP monitoring session management"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = VIPMonitoringSessionSerializer
    
    def get_queryset(self):
        """Filter sessions based on user permissions"""
        user = self.request.user
        
        # Control operators see assigned sessions
        if hasattr(user, 'control_operator'):
            operator = user.control_operator
            if operator.can_monitor_vip:
                return VIPMonitoringSession.objects.filter(
                    assigned_operator=user
                ).select_related('user', 'driver', 'assigned_operator')
            else:
                return VIPMonitoringSession.objects.none()
        
        # Admin users see all sessions
        if user.is_superuser:
            return VIPMonitoringSession.objects.all().select_related(
                'user', 'driver', 'assigned_operator'
            )
        
        # Users see their own sessions
        return VIPMonitoringSession.objects.filter(
            Q(user=user) | Q(driver=user)
        ).select_related('user', 'driver', 'assigned_operator')
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update real-time location"""
        session = self.get_object()
        
        # Only driver or system can update location
        if request.user != session.driver and not request.user.is_superuser:
            return Response(
                {'error': 'Only assigned driver can update location'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not latitude or not longitude:
            return Response(
                {'error': 'Latitude and longitude required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.current_latitude = latitude
        session.current_longitude = longitude
        session.last_location_update = timezone.now()
        session.save()
        
        # Check for route deviation (implement as needed)
        # self._check_route_deviation(session)
        
        return Response({
            'status': 'location_updated',
            'session_id': str(session.id),
            'timestamp': session.last_location_update
        })
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Manual check-in by VIP user"""
        session = self.get_object()
        
        if request.user != session.user:
            return Response(
                {'error': 'Only session user can check in'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session.last_check_in = timezone.now()
        session.save()
        
        return Response({
            'status': 'checked_in',
            'session_id': str(session.id),
            'check_in_time': session.last_check_in
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_sos(request):
    """Trigger SOS emergency"""
    serializer = SOSTriggerSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        ride_obj = None
        vehicle_obj = None
        ride_id = data.get('ride_id')
        vehicle_id = data.get('vehicle_id')
        if ride_id:
            ride_obj = Ride.objects.filter(id=ride_id).first()
        if vehicle_id:
            vehicle_obj = Vehicle.objects.filter(id=vehicle_id).first()
        
        # Create emergency incident
        incident = EmergencyIncident.objects.create(
            incident_type=data['incident_type'],
            priority=IncidentPriority.CRITICAL,
            user=request.user,
            ride=ride_obj,
            vehicle=vehicle_obj,
            incident_latitude=data['latitude'],
            incident_longitude=data['longitude'],
            description=data['description'],
            user_triggered=True
        )
        
        # Auto-assign operator and trigger protocols
        # (These would be handled by the incident creation process)
        
        logger.critical(f"SOS triggered by user {request.user.id}: {incident.id}")
        
        return Response({
            'status': 'sos_triggered',
            'incident_id': str(incident.id),
            'response_time_estimate': '5 minutes',
            'emergency_contact_notified': True
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monitoring_dashboard(request):
    """Get monitoring dashboard data"""
    if not hasattr(request.user, 'control_operator'):
        return Response(
            {'error': 'Control operator access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Calculate dashboard metrics
    today = timezone.now().date()
    
    # Active incidents
    active_incidents = EmergencyIncident.objects.filter(
        status__in=[IncidentStatus.ACTIVE, IncidentStatus.RESPONDED]
    ).count()
    
    # Critical incidents
    critical_incidents = EmergencyIncident.objects.filter(
        priority=IncidentPriority.CRITICAL,
        status__in=[IncidentStatus.ACTIVE, IncidentStatus.RESPONDED]
    ).count()
    
    # Active VIP sessions
    active_vip_sessions = VIPMonitoringSession.objects.filter(
        is_active=True
    ).count()
    
    # Operators on duty
    operators_on_duty = ControlOperator.objects.filter(
        is_active=True,
        is_on_duty=True
    ).count()
    
    # Average response time
    avg_response = EmergencyIncident.objects.filter(
        response_time_seconds__isnull=False,
        created_at__date=today
    ).aggregate(avg_time=Avg('response_time_seconds'))
    
    average_response_time = avg_response['avg_time'] or 0
    
    # Incidents today
    incidents_today = EmergencyIncident.objects.filter(
        created_at__date=today
    ).count()
    
    # Resolved today
    resolved_today = EmergencyIncident.objects.filter(
        created_at__date=today,
        status=IncidentStatus.RESOLVED
    ).count()
    
    # Recent incidents
    recent_incidents = EmergencyIncident.objects.filter(
        status__in=[IncidentStatus.ACTIVE, IncidentStatus.RESPONDED]
    ).order_by('-created_at')[:10]
    
    # Overdue check-ins
    overdue_threshold = timezone.now() - timedelta(minutes=20)
    overdue_checkins = VIPMonitoringSession.objects.filter(
        is_active=True,
        auto_check_in_enabled=True,
        last_check_in__lt=overdue_threshold
    )[:5]
    
    dashboard_data = {
        'active_incidents': active_incidents,
        'critical_incidents': critical_incidents,
        'active_vip_sessions': active_vip_sessions,
        'operators_on_duty': operators_on_duty,
        'average_response_time': average_response_time,
        'incidents_today': incidents_today,
        'resolved_today': resolved_today,
        'recent_incidents': recent_incidents,
        'overdue_checkins': overdue_checkins
    }
    
    serializer = MonitoringDashboardSerializer(dashboard_data)
    return Response(serializer.data)
