# GPS Encryption Celery Tasks
"""
Background tasks for GPS encryption system
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from celery.exceptions import Retry

from core.encryption import GPSEncryptionManager
from core.gps_models import (
    GPSEncryptionSession,
    EncryptedGPSData,
    GPSEncryptionAudit,
    GPSDataRetentionSchedule
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_expired_sessions(self):
    """Clean up expired GPS encryption sessions"""
    try:
        # Find expired but still active sessions
        expired_sessions = GPSEncryptionSession.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        
        cleaned_count = 0
        encryption_manager = GPSEncryptionManager()
        
        for session in expired_sessions:
            try:
                # End session in database
                session.end_session()
                
                # Clear from encryption manager
                encryption_manager.end_encryption_session(session.session_id)
                
                # Log cleanup
                GPSEncryptionAudit.objects.create(
                    event_type='session_expired',
                    severity='info',
                    message=f'Auto-cleanup expired session {session.session_id}',
                    session=session,
                    metadata={
                        'cleanup_type': 'automatic',
                        'session_duration_minutes': int(
                            (session.expires_at - session.created_at)
                            .total_seconds() / 60
                        )
                    }
                )
                
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"Error cleaning session {session.session_id}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} expired sessions")
        return {'cleaned_count': cleaned_count}
        
    except Exception as exc:
        logger.error(f"Session cleanup task failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def process_data_retention(self, schedule_id=None):
    """Process GPS data retention policies"""
    try:
        # Get active retention schedules
        schedules = GPSDataRetentionSchedule.objects.filter(
            is_active=True,
            next_run__lte=timezone.now()
        )
        
        if schedule_id:
            schedules = schedules.filter(id=schedule_id)
        
        processed_schedules = []
        
        for schedule in schedules:
            try:
                # Calculate cutoff date
                cutoff_date = timezone.now() - timedelta(
                    days=schedule.retention_days
                )
                
                # Find data to process
                data_query = EncryptedGPSData.objects.filter(
                    recorded_at__lt=cutoff_date
                )
                
                # Apply user tier filter if specified
                if schedule.user_tier and not schedule.applies_to_all:
                    data_query = data_query.filter(
                        user__tier=schedule.user_tier
                    )
                
                data_count = data_query.count()
                processed_count = 0
                failed_count = 0
                
                # Process data according to retention action
                if schedule.action == 'delete':
                    deleted_count = data_query.delete()[0]
                    processed_count = deleted_count
                    
                elif schedule.action == 'anonymize':
                    # Anonymize GPS data (remove user association)
                    for data_item in data_query.iterator(chunk_size=100):
                        try:
                            data_item.user = None
                            data_item.save()
                            processed_count += 1
                        except Exception as e:
                            logger.error(f"Failed to anonymize data {data_item.id}: {e}")
                            failed_count += 1
                
                elif schedule.action == 'archive':
                    # Move to archive storage (implement as needed)
                    logger.info(f"Archive action not implemented for schedule {schedule.id}")
                
                # Update schedule statistics
                schedule.records_processed += processed_count
                schedule.records_failed += failed_count
                schedule.last_run = timezone.now()
                schedule.next_run = timezone.now() + timedelta(hours=24)
                schedule.save()
                
                # Log retention processing
                GPSEncryptionAudit.objects.create(
                    event_type='system_error' if failed_count > 0 else 'info',
                    severity='warning' if failed_count > 0 else 'info',
                    message=f'Data retention processed: {schedule.name}',
                    metadata={
                        'schedule_id': str(schedule.id),
                        'total_records': data_count,
                        'processed_count': processed_count,
                        'failed_count': failed_count,
                        'action': schedule.action,
                        'retention_days': schedule.retention_days
                    }
                )
                
                processed_schedules.append({
                    'schedule_id': str(schedule.id),
                    'name': schedule.name,
                    'processed_count': processed_count,
                    'failed_count': failed_count
                })
                
            except Exception as e:
                logger.error(f"Error processing retention schedule {schedule.id}: {e}")
                schedule.records_failed += 1
                schedule.save()
        
        return {'processed_schedules': processed_schedules}
        
    except Exception as exc:
        logger.error(f"Data retention task failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def encrypt_gps_batch(self, gps_data_batch, session_id):
    """Encrypt a batch of GPS coordinates in background"""
    try:
        encryption_manager = GPSEncryptionManager()
        results = []
        
        for gps_data in gps_data_batch:
            try:
                result = encryption_manager.encrypt_gps_data(
                    session_id=session_id,
                    gps_data=gps_data
                )
                results.append({
                    'success': result['success'],
                    'timestamp': gps_data.get('timestamp'),
                    'encrypted_data': result.get('encrypted_data'),
                    'nonce': result.get('nonce'),
                    'error': result.get('error')
                })
                
            except Exception as e:
                logger.error(f"Batch encryption error for GPS data: {e}")
                results.append({
                    'success': False,
                    'timestamp': gps_data.get('timestamp'),
                    'error': str(e)
                })
        
        return {'results': results}
        
    except Exception as exc:
        logger.error(f"GPS batch encryption task failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def decrypt_gps_batch(self, encrypted_data_ids, requester_id, reason):
    """Decrypt a batch of GPS data in background"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        requester = User.objects.get(id=requester_id)
        encryption_manager = GPSEncryptionManager()
        results = []
        
        # Get encrypted data
        encrypted_data = EncryptedGPSData.objects.filter(
            id__in=encrypted_data_ids
        ).select_related('session', 'user')
        
        for data_item in encrypted_data:
            try:
                # Check permissions
                if not requester.is_staff and data_item.user != requester:
                    results.append({
                        'data_id': str(data_item.id),
                        'success': False,
                        'error': 'Permission denied'
                    })
                    continue
                
                # Decrypt data
                result = encryption_manager.decrypt_gps_data(
                    session_id=data_item.session.session_id,
                    encrypted_data=data_item.encrypted_data,
                    nonce=data_item.nonce
                )
                
                if result['success']:
                    gps_coords = result['gps_data']
                    results.append({
                        'data_id': str(data_item.id),
                        'success': True,
                        'latitude': gps_coords.latitude,
                        'longitude': gps_coords.longitude,
                        'timestamp': data_item.timestamp.isoformat(),
                        'speed': gps_coords.speed,
                        'bearing': gps_coords.bearing,
                        'altitude': gps_coords.altitude,
                        'accuracy': gps_coords.accuracy
                    })
                else:
                    results.append({
                        'data_id': str(data_item.id),
                        'success': False,
                        'error': result['error']
                    })
                
                # Log decryption attempt
                from core.gps_models import GPSDecryptionLog
                GPSDecryptionLog.objects.create(
                    gps_data=data_item,
                    requested_by=requester,
                    request_reason=reason,
                    status='success' if result['success'] else 'failed',
                    error_message=result.get('error', ''),
                    decryption_time_ms=result.get('decryption_time_ms', 0)
                )
                
            except Exception as e:
                logger.error(f"Batch decryption error for {data_item.id}: {e}")
                results.append({
                    'data_id': str(data_item.id),
                    'success': False,
                    'error': str(e)
                })
        
        return {'results': results}
        
    except Exception as exc:
        logger.error(f"GPS batch decryption task failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_encryption_report(self, report_type, start_date, end_date, user_id=None):
    """Generate GPS encryption system reports"""
    try:
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Avg
        
        User = get_user_model()
        report_data = {}
        
        # Date range filter
        date_filter = {
            'created_at__gte': start_date,
            'created_at__lte': end_date
        }
        
        if report_type == 'session_summary':
            # Session statistics
            sessions = GPSEncryptionSession.objects.filter(**date_filter)
            
            if user_id:
                sessions = sessions.filter(ride__user_id=user_id)
            
            report_data = {
                'total_sessions': sessions.count(),
                'active_sessions': sessions.filter(is_active=True).count(),
                'completed_sessions': sessions.filter(is_active=False).count(),
                'avg_duration_minutes': sessions.aggregate(
                    avg_duration=Avg('id')  # Proper calculation needed
                )['avg_duration'] or 0,
                'total_encryptions': sum(s.encryption_count for s in sessions),
                'total_decryptions': sum(s.decryption_count for s in sessions)
            }
        
        elif report_type == 'security_audit':
            # Security audit report
            audit_events = GPSEncryptionAudit.objects.filter(**date_filter)
            
            report_data = {
                'total_events': audit_events.count(),
                'events_by_type': dict(
                    audit_events.values_list('event_type')
                    .annotate(count=Count('id'))
                    .values_list('event_type', 'count')
                ),
                'events_by_severity': dict(
                    audit_events.values_list('severity')
                    .annotate(count=Count('id'))
                    .values_list('severity', 'count')
                ),
                'critical_events': audit_events.filter(
                    severity='critical'
                ).count(),
                'failed_operations': audit_events.filter(
                    event_type__in=['encryption_failed', 'decryption_failed']
                ).count()
            }
        
        elif report_type == 'data_usage':
            # Data usage report
            encrypted_data = EncryptedGPSData.objects.filter(
                recorded_at__gte=start_date,
                recorded_at__lte=end_date
            )
            
            if user_id:
                encrypted_data = encrypted_data.filter(user_id=user_id)
            
            report_data = {
                'total_data_points': encrypted_data.count(),
                'data_by_user_tier': dict(
                    encrypted_data.values_list('user__tier')
                    .annotate(count=Count('id'))
                    .values_list('user__tier', 'count')
                ),
                'data_by_device': dict(
                    encrypted_data.values_list('source_device')
                    .annotate(count=Count('id'))
                    .values_list('source_device', 'count')
                ),
                'avg_points_per_session': (
                    encrypted_data.count() / 
                    GPSEncryptionSession.objects.filter(**date_filter).count()
                ) if GPSEncryptionSession.objects.filter(**date_filter).count() > 0 else 0
            }
        
        # Log report generation
        GPSEncryptionAudit.objects.create(
            event_type='system_error',
            severity='info',
            message=f'Generated {report_type} report',
            metadata={
                'report_type': report_type,
                'start_date': start_date,
                'end_date': end_date,
                'user_id': user_id,
                'data_points': len(report_data)
            }
        )
        
        return {
            'report_type': report_type,
            'generated_at': timezone.now().isoformat(),
            'data': report_data
        }
        
    except Exception as exc:
        logger.error(f"Report generation task failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def monitor_encryption_performance(self):
    """Monitor GPS encryption system performance"""
    try:
        # Calculate performance metrics
        recent_time = timezone.now() - timedelta(hours=1)
        
        # Session metrics
        active_sessions = GPSEncryptionSession.objects.filter(
            is_active=True
        ).count()
        
        recent_encryptions = EncryptedGPSData.objects.filter(
            recorded_at__gte=recent_time
        ).count()
        
        recent_failures = GPSEncryptionAudit.objects.filter(
            created_at__gte=recent_time,
            event_type__in=['encryption_failed', 'decryption_failed']
        ).count()
        
        # Calculate success rate
        total_recent_ops = recent_encryptions + recent_failures
        success_rate = (
            (recent_encryptions / total_recent_ops * 100)
            if total_recent_ops > 0 else 100
        )
        
        # Performance thresholds
        performance_data = {
            'timestamp': timezone.now().isoformat(),
            'active_sessions': active_sessions,
            'recent_encryptions': recent_encryptions,
            'recent_failures': recent_failures,
            'success_rate': success_rate,
            'alerts': []
        }
        
        # Check for performance issues
        if success_rate < 95:
            performance_data['alerts'].append({
                'type': 'low_success_rate',
                'message': f'Encryption success rate below 95%: {success_rate:.1f}%',
                'severity': 'warning'
            })
        
        if active_sessions > getattr(settings, 'GPS_MAX_CONCURRENT_SESSIONS', 1000):
            performance_data['alerts'].append({
                'type': 'high_session_count',
                'message': f'High number of active sessions: {active_sessions}',
                'severity': 'warning'
            })
        
        if recent_failures > 10:
            performance_data['alerts'].append({
                'type': 'high_failure_rate',
                'message': f'High number of recent failures: {recent_failures}',
                'severity': 'error'
            })
        
        # Log performance alerts
        for alert in performance_data['alerts']:
            GPSEncryptionAudit.objects.create(
                event_type='system_error',
                severity=alert['severity'],
                message=f"Performance alert: {alert['message']}",
                metadata={
                    'alert_type': alert['type'],
                    'performance_data': performance_data
                }
            )
        
        logger.info(f"Performance monitoring: {performance_data}")
        return performance_data
        
    except Exception as exc:
        logger.error(f"Performance monitoring task failed: {exc}")
        raise self.retry(exc=exc)


# Periodic task schedule (add to Django settings)
"""
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-gps-sessions': {
        'task': 'core.gps_tasks.cleanup_expired_sessions',
        'schedule': 300.0,  # Every 5 minutes
    },
    'process-gps-data-retention': {
        'task': 'core.gps_tasks.process_data_retention',
        'schedule': 3600.0,  # Every hour
    },
    'monitor-gps-encryption-performance': {
        'task': 'core.gps_tasks.monitor_encryption_performance',
        'schedule': 900.0,  # Every 15 minutes
    },
}
"""
