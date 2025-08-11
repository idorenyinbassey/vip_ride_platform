# rides/management/commands/process_workflow_actions.py
"""
Django management command to process pending workflow actions
Run this periodically via cron or Celery for automatic workflow processing
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from rides.status_models import WorkflowAction
from rides.workflow import RideWorkflow, RideWorkflowManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process pending workflow actions for rides'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action-type',
            type=str,
            help='Process only specific action type',
        )
        parser.add_argument(
            '--max-actions',
            type=int,
            default=100,
            help='Maximum number of actions to process',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )
    
    def handle(self, *args, **options):
        action_type = options.get('action_type')
        max_actions = options.get('max_actions')
        dry_run = options.get('dry_run')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processing workflow actions (max: {max_actions})'
            )
        )
        
        # Get pending actions
        queryset = WorkflowAction.objects.filter(
            action_status__in=[
                WorkflowAction.ActionStatus.PENDING,
                WorkflowAction.ActionStatus.FAILED
            ],
            scheduled_at__lte=timezone.now()
        )
        
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Include retry actions
        retry_queryset = WorkflowAction.objects.filter(
            action_status=WorkflowAction.ActionStatus.PENDING,
            next_retry_at__lte=timezone.now(),
            retry_count__lt=models.F('max_retries')
        )
        
        queryset = queryset.union(retry_queryset)
        queryset = queryset.order_by('scheduled_at')[:max_actions]
        
        processed_count = 0
        success_count = 0
        error_count = 0
        
        for action in queryset:
            if dry_run:
                self.stdout.write(
                    f'Would process: {action.ride.id} - {action.action_type}'
                )
                continue
            
            try:
                with transaction.atomic():
                    result = self.process_action(action)
                    if result:
                        success_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Processed {action.action_type} for ride {action.ride.id}'
                            )
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Failed {action.action_type} for ride {action.ride.id}'
                            )
                        )
                    
                    processed_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f'Error processing action {action.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error processing {action.action_type}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Completed: {processed_count} processed, '
                f'{success_count} successful, {error_count} errors'
            )
        )
    
    def process_action(self, action: WorkflowAction) -> bool:
        """Process a single workflow action"""
        try:
            action.mark_started()
            
            if action.action_type == WorkflowAction.ActionType.STATUS_TRANSITION:
                return self.process_status_transition(action)
            elif action.action_type == WorkflowAction.ActionType.DRIVER_SEARCH:
                return self.process_driver_search(action)
            elif action.action_type == WorkflowAction.ActionType.PAYMENT_PROCESS:
                return self.process_payment(action)
            elif action.action_type == WorkflowAction.ActionType.NOTIFICATION_SEND:
                return self.process_notification(action)
            elif action.action_type == WorkflowAction.ActionType.CANCELLATION_FEE:
                return self.process_cancellation_fee(action)
            elif action.action_type == WorkflowAction.ActionType.GPS_TRACKING_START:
                return self.process_gps_tracking(action)
            elif action.action_type == WorkflowAction.ActionType.SOS_TRIGGER:
                return self.process_sos_trigger(action)
            else:
                action.mark_failed(f'Unknown action type: {action.action_type}')
                return False
                
        except Exception as e:
            action.mark_failed(str(e))
            return False
    
    def process_status_transition(self, action: WorkflowAction) -> bool:
        """Process automatic status transition"""
        try:
            workflow = RideWorkflow(action.ride)
            target_status = action.action_data.get('target_status')
            reason = action.action_data.get('reason', 'Automatic transition')
            
            if not target_status:
                action.mark_failed('No target status specified')
                return False
            
            from rides.workflow import RideStatus
            new_status = RideStatus(target_status)
            
            success = workflow.transition_to(new_status, reason=reason)
            
            if success:
                action.mark_completed({'status_changed': True})
                return True
            else:
                action.mark_failed('Status transition failed')
                return False
                
        except Exception as e:
            action.mark_failed(f'Status transition error: {str(e)}')
            return False
    
    def process_driver_search(self, action: WorkflowAction) -> bool:
        """Process driver search action"""
        try:
            from rides.matching import RideMatchingService
            
            matching_service = RideMatchingService()
            result = matching_service.find_drivers_for_ride(action.ride)
            
            if result:
                action.mark_completed({
                    'drivers_found': len(result.get('drivers', [])),
                    'matching_result': result
                })
                return True
            else:
                action.mark_failed('No drivers found')
                return False
                
        except Exception as e:
            action.mark_failed(f'Driver search error: {str(e)}')
            return False
    
    def process_payment(self, action: WorkflowAction) -> bool:
        """Process payment workflow action"""
        try:
            from payments.services import PaymentService
            
            payment_service = PaymentService()
            result = payment_service.process_ride_payment(action.ride)
            
            if result and result.get('success'):
                action.mark_completed({'payment_result': result})
                
                # Update ride status
                workflow = RideWorkflow(action.ride)
                from rides.workflow import RideStatus
                workflow.transition_to(RideStatus.PAYMENT_COMPLETED)
                
                return True
            else:
                action.mark_failed('Payment processing failed')
                
                # Update ride status
                workflow = RideWorkflow(action.ride)
                from rides.workflow import RideStatus
                workflow.transition_to(RideStatus.PAYMENT_FAILED)
                
                return False
                
        except Exception as e:
            action.mark_failed(f'Payment error: {str(e)}')
            return False
    
    def process_notification(self, action: WorkflowAction) -> bool:
        """Process notification sending"""
        try:
            from notifications.services import NotificationService
            
            notification_service = NotificationService()
            notification_data = action.action_data
            
            result = notification_service.send_notification(
                user_id=notification_data.get('user_id'),
                message_type=notification_data.get('message_type'),
                data=notification_data.get('data', {})
            )
            
            if result:
                action.mark_completed({'notification_sent': True})
                return True
            else:
                action.mark_failed('Notification sending failed')
                return False
                
        except Exception as e:
            action.mark_failed(f'Notification error: {str(e)}')
            return False
    
    def process_cancellation_fee(self, action: WorkflowAction) -> bool:
        """Process cancellation fee charging"""
        try:
            from payments.services import PaymentService
            from rides.workflow import CancellationPolicy
            
            fee_amount = action.action_data.get('fee_amount')
            user_tier = action.action_data.get('user_tier', 'normal')
            
            if not fee_amount or fee_amount <= 0:
                action.mark_completed({'fee_amount': 0, 'charged': False})
                return True
            
            payment_service = PaymentService()
            result = payment_service.charge_cancellation_fee(
                action.ride, 
                fee_amount
            )
            
            if result:
                action.mark_completed({
                    'fee_charged': True,
                    'amount': fee_amount
                })
                return True
            else:
                action.mark_failed('Cancellation fee charge failed')
                return False
                
        except Exception as e:
            action.mark_failed(f'Cancellation fee error: {str(e)}')
            return False
    
    def process_gps_tracking(self, action: WorkflowAction) -> bool:
        """Process GPS tracking initiation"""
        try:
            from gps_tracking.services import GPSTrackingService
            
            gps_service = GPSTrackingService()
            result = gps_service.start_ride_tracking(action.ride)
            
            if result:
                action.mark_completed({'tracking_started': True})
                return True
            else:
                action.mark_failed('GPS tracking start failed')
                return False
                
        except Exception as e:
            action.mark_failed(f'GPS tracking error: {str(e)}')
            return False
    
    def process_sos_trigger(self, action: WorkflowAction) -> bool:
        """Process SOS emergency trigger"""
        try:
            from control_center.services import EmergencyService
            
            emergency_service = EmergencyService()
            result = emergency_service.handle_sos_trigger(action.ride)
            
            if result:
                action.mark_completed({'sos_processed': True})
                return True
            else:
                action.mark_failed('SOS processing failed')
                return False
                
        except Exception as e:
            action.mark_failed(f'SOS error: {str(e)}')
            return False
