# rides/workflow_views.py
"""
VIP Ride-Hailing Platform - Workflow API Views
REST API endpoints for ride workflow management
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from typing import Dict, Any
import logging

from .models import Ride
from .workflow import (
    RideWorkflow, RideWorkflowManager, RideStatus, 
    CancellationPolicy, RideWorkflowError
)
from .serializers import RideSerializer, RideStatusHistorySerializer
from accounts.permissions import TierBasedPermission, VIPOnlyPermission

logger = logging.getLogger(__name__)


class RideRequestView(APIView):
    """Create new ride request and start workflow"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create new ride request"""
        try:
            data = request.data
            
            # Validate required fields
            required_fields = [
                'pickup_latitude', 'pickup_longitude',
                'destination_latitude', 'destination_longitude'
            ]
            
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Prepare location data
            pickup_location = {
                'latitude': float(data['pickup_latitude']),
                'longitude': float(data['pickup_longitude']),
                'address': data.get('pickup_address', '')
            }
            
            destination_location = {
                'latitude': float(data['destination_latitude']),
                'longitude': float(data['destination_longitude']),
                'address': data.get('destination_address', '')
            }
            
            ride_type = data.get('ride_type', 'normal')
            
            # Create ride through workflow manager
            ride = RideWorkflowManager.request_ride(
                rider=request.user,
                pickup_location=pickup_location,
                destination_location=destination_location,
                ride_type=ride_type
            )
            
            # Serialize and return
            serializer = RideSerializer(ride)
            
            return Response({
                'success': True,
                'message': 'Ride requested successfully',
                'ride': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': f'Invalid data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except RideWorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f'Error creating ride request: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DriverAcceptanceView(APIView):
    """Handle driver acceptance/rejection of rides"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, ride_id):
        """Driver accept ride"""
        try:
            ride = get_object_or_404(Ride, id=ride_id)
            
            # Check if user is a driver
            if not hasattr(request.user, 'driver'):
                return Response(
                    {'error': 'Only drivers can accept rides'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            success = RideWorkflowManager.driver_accept_ride(
                ride=ride,
                driver_user=request.user
            )
            
            if success:
                serializer = RideSerializer(ride)
                return Response({
                    'success': True,
                    'message': 'Ride accepted successfully',
                    'ride': serializer.data
                })
            else:
                return Response(
                    {'error': 'Failed to accept ride'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f'Error accepting ride: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, ride_id):
        """Driver reject ride"""
        try:
            ride = get_object_or_404(Ride, id=ride_id)
            reason = request.data.get('reason', 'Driver declined')
            
            # Check if user is a driver
            if not hasattr(request.user, 'driver'):
                return Response(
                    {'error': 'Only drivers can reject rides'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            success = RideWorkflowManager.driver_reject_ride(
                ride=ride,
                driver_user=request.user,
                reason=reason
            )
            
            if success:
                return Response({
                    'success': True,
                    'message': 'Ride rejected successfully'
                })
            else:
                return Response(
                    {'error': 'Failed to reject ride'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f'Error rejecting ride: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RideCancellationView(APIView):
    """Handle ride cancellation with policy checks"""
    
    permission_classes = [permissions.IsAuthenticated, TierBasedPermission]
    
    def post(self, request, ride_id):
        """Cancel ride"""
        try:
            ride = get_object_or_404(Ride, id=ride_id)
            reason = request.data.get('reason', 'User cancelled')
            
            # Check authorization
            if request.user != ride.rider and (
                not hasattr(request.user, 'driver') or 
                request.user.driver != ride.driver
            ):
                return Response(
                    {'error': 'Not authorized to cancel this ride'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            success, message = RideWorkflowManager.cancel_ride(
                ride=ride,
                user=request.user,
                reason=reason
            )
            
            if success:
                serializer = RideSerializer(ride)
                return Response({
                    'success': True,
                    'message': message,
                    'ride': serializer.data
                })
            else:
                return Response(
                    {'error': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f'Error cancelling ride: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RideStatusUpdateView(APIView):
    """Update ride status (driver actions)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, ride_id):
        """Update ride status"""
        try:
            ride = get_object_or_404(Ride, id=ride_id)
            new_status = request.data.get('status')
            
            if not new_status:
                return Response(
                    {'error': 'Status is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check authorization - only assigned driver can update
            if (not hasattr(request.user, 'driver') or 
                request.user.driver != ride.driver):
                return Response(
                    {'error': 'Only assigned driver can update ride status'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate status transition
            workflow = RideWorkflow(ride)
            target_status = RideStatus(new_status)
            
            if not workflow.can_transition_to(target_status):
                return Response(
                    {'error': f'Invalid status transition to {new_status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform transition
            success = workflow.transition_to(
                target_status, 
                user=request.user,
                reason=request.data.get('reason', 'Driver update')
            )
            
            if success:
                serializer = RideSerializer(ride)
                return Response({
                    'success': True,
                    'message': f'Status updated to {new_status}',
                    'ride': serializer.data
                })
            else:
                return Response(
                    {'error': 'Failed to update status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValueError:
            return Response(
                {'error': 'Invalid status value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f'Error updating ride status: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RideCompletionView(APIView):
    """Handle ride completion workflow"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, ride_id):
        """Driver mark ride as completed"""
        try:
            ride = get_object_or_404(Ride, id=ride_id)
            
            # Check authorization
            if (not hasattr(request.user, 'driver') or 
                request.user.driver != ride.driver):
                return Response(
                    {'error': 'Only assigned driver can complete ride'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            success = RideWorkflowManager.complete_ride(
                ride=ride,
                driver_user=request.user
            )
            
            if success:
                serializer = RideSerializer(ride)
                return Response({
                    'success': True,
                    'message': 'Ride completed successfully',
                    'ride': serializer.data
                })
            else:
                return Response(
                    {'error': 'Failed to complete ride'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f'Error completing ride: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RideStatusHistoryView(APIView):
    """Get ride status change history"""
    
    permission_classes = [permissions.IsAuthenticated, TierBasedPermission]
    
    def get(self, request, ride_id):
        """Get status history for ride"""
        try:
            ride = get_object_or_404(Ride, id=ride_id)
            
            # Check authorization
            if (request.user != ride.rider and 
                (not hasattr(request.user, 'driver') or 
                 request.user.driver != ride.driver)):
                return Response(
                    {'error': 'Not authorized to view this ride'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            history = ride.status_history.all()
            serializer = RideStatusHistorySerializer(history, many=True)
            
            return Response({
                'success': True,
                'history': serializer.data
            })
            
        except Exception as e:
            logger.error(f'Error getting ride history: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancellationPolicyView(APIView):
    """Get cancellation policy for user"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, ride_id=None):
        """Get cancellation policy information"""
        try:
            user_tier = getattr(request.user, 'tier', 'normal')
            policy = CancellationPolicy.get_policy(user_tier)
            
            response_data = {
                'success': True,
                'policy': policy,
                'user_tier': user_tier
            }
            
            if ride_id:
                ride = get_object_or_404(Ride, id=ride_id)
                
                # Check authorization
                if request.user != ride.rider:
                    return Response(
                        {'error': 'Not authorized'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                can_cancel_free, fee_message = CancellationPolicy.can_cancel_free(
                    ride, user_tier
                )
                can_cancel_daily, limit_message = CancellationPolicy.check_daily_cancellation_limit(
                    request.user, user_tier
                )
                
                response_data.update({
                    'can_cancel_free': can_cancel_free,
                    'fee_message': fee_message,
                    'can_cancel_daily': can_cancel_daily,
                    'limit_message': limit_message
                })
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f'Error getting cancellation policy: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_active_rides(request):
    """Get user's active rides"""
    try:
        from rides.workflow import get_user_active_rides
        
        active_rides = get_user_active_rides(request.user)
        serializer = RideSerializer(active_rides, many=True)
        
        return Response({
            'success': True,
            'active_rides': serializer.data,
            'count': len(active_rides)
        })
        
    except Exception as e:
        logger.error(f'Error getting active rides: {str(e)}')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ride_workflow_status(request, ride_id):
    """Get detailed workflow status for ride"""
    try:
        ride = get_object_or_404(Ride, id=ride_id)
        
        # Check authorization
        if (request.user != ride.rider and 
            (not hasattr(request.user, 'driver') or 
             request.user.driver != ride.driver)):
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        workflow = RideWorkflow(ride)
        
        # Get possible next transitions
        possible_transitions = []
        for next_status in RideStatus:
            if workflow.can_transition_to(next_status):
                possible_transitions.append({
                    'status': next_status.value,
                    'display': next_status.name
                })
        
        # Get workflow actions
        recent_actions = ride.workflow_actions.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        )[:10]
        
        return Response({
            'success': True,
            'current_status': workflow.current_status.value,
            'possible_transitions': possible_transitions,
            'recent_actions': [
                {
                    'action_type': action.action_type,
                    'status': action.action_status,
                    'created_at': action.created_at,
                    'error_message': action.error_message
                }
                for action in recent_actions
            ]
        })
        
    except Exception as e:
        logger.error(f'Error getting workflow status: {str(e)}')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, VIPOnlyPermission])
def trigger_sos(request, ride_id):
    """Trigger SOS emergency protocol (VIP only)"""
    try:
        ride = get_object_or_404(Ride, id=ride_id)
        
        # Check authorization - only rider can trigger SOS
        if request.user != ride.rider:
            return Response(
                {'error': 'Only the rider can trigger SOS'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if VIP ride
        if ride.rider_tier != 'vip':
            return Response(
                {'error': 'SOS feature only available for VIP users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Trigger SOS
        ride.trigger_sos()
        
        # Create workflow action for SOS processing
        from rides.status_models import WorkflowAction
        WorkflowAction.objects.create(
            ride=ride,
            action_type=WorkflowAction.ActionType.SOS_TRIGGER,
            triggered_by_status=ride.status,
            action_data={
                'triggered_by': request.user.id,
                'trigger_time': timezone.now().isoformat(),
                'emergency_type': request.data.get('emergency_type', 'general')
            }
        )
        
        return Response({
            'success': True,
            'message': 'SOS triggered successfully. Emergency services have been notified.',
            'sos_reference': str(ride.id)
        })
        
    except Exception as e:
        logger.error(f'Error triggering SOS: {str(e)}')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
