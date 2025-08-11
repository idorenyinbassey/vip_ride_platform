# payments/management/commands/process_driver_payouts.py
"""
Management command to process scheduled driver payouts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import logging
from decimal import Decimal
from datetime import timedelta
from payments.payment_models import DriverPayout, PaymentAuditLog
from payments.services import DriverPayoutService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process scheduled driver payouts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually processing'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of payouts to process in each batch'
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Maximum number of retries for failed payouts'
        )
        parser.add_argument(
            '--driver-id',
            type=str,
            help='Process payouts for specific driver only'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        max_retries = options['max_retries']
        driver_id = options.get('driver_id')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No actual processing will occur')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Starting driver payout processing...')
        )
        
        try:
            # Get payouts ready for processing
            payouts_query = DriverPayout.objects.filter(
                status=DriverPayout.PayoutStatus.SCHEDULED,
                scheduled_date__lte=timezone.now(),
                retry_count__lt=max_retries
            ).select_related('driver', 'currency', 'gateway')
            
            if driver_id:
                payouts_query = payouts_query.filter(driver_id=driver_id)
            
            total_payouts = payouts_query.count()
            
            if total_payouts == 0:
                self.stdout.write(
                    self.style.SUCCESS('No payouts ready for processing')
                )
                return
            
            self.stdout.write(
                f'Found {total_payouts} payouts ready for processing'
            )
            
            # Process payouts in batches using iterator for efficiency
            processed_count = 0
            failed_count = 0
            
            payout_service = DriverPayoutService()
            
            # Use iterator to avoid offset issues and memory efficiency
            batch = []
            for payout in payouts_query.iterator(chunk_size=batch_size):
                batch.append(payout)
                
                if len(batch) >= batch_size:
                    self._process_batch(batch, dry_run, payout_service, processed_count, failed_count)
                    processed_count += len([p for p in batch if self._payout_processed_successfully(p)])
                    failed_count += len([p for p in batch if not self._payout_processed_successfully(p)])
                    batch = []
            
            # Process remaining items in the last batch
            if batch:
                self._process_batch(batch, dry_run, payout_service, processed_count, failed_count)
                processed_count += len([p for p in batch if self._payout_processed_successfully(p)])
                failed_count += len([p for p in batch if not self._payout_processed_successfully(p)])
                        failed_count += 1
                        logger.error(
                            f"Failed to process payout {payout.id}: {str(e)}"
                        )
                        self.stdout.write(
                            self.style.ERROR(
                                f'Failed to process payout {payout.id}: {str(e)}'
                            )
                        )
                        
                        if not dry_run:
                            # Update payout with failure info
                            with transaction.atomic():
                                payout.failure_reason = str(e)[:500]
                                payout.retry_count += 1
                                if payout.retry_count >= max_retries:
                                    payout.status = DriverPayout.PayoutStatus.FAILED
                                payout.save()
                                
                                # Log the failure
                                PaymentAuditLog.objects.create(
                                    action_type='payout_failed',
                                    description=f'Payout processing failed: {str(e)}',
                                    payout=payout,
                                    metadata={'retry_count': payout.retry_count}
                                )
            
            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'Payout processing completed: '
                    f'{processed_count} processed, {failed_count} failed'
                )
            )
            
        except Exception as e:
            logger.error(f"Payout processing command failed: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Payout processing failed: {str(e)}')
            )
    
    def process_single_payout(self, payout, payout_service):
        """Process a single payout"""
        with transaction.atomic():
            # Update status to processing
            payout.status = DriverPayout.PayoutStatus.PROCESSING
            payout.processed_date = timezone.now()
            payout.save()
            
            # Log processing start
            PaymentAuditLog.objects.create(
                action_type='payout_processing_started',
                description=f'Started processing payout for driver {payout.driver.id}',
                payout=payout,
                metadata={
                    'amount': str(payout.net_payout_amount),
                    'currency': payout.currency.code,
                    'gateway': payout.gateway.name if payout.gateway else None
                }
            )
        
        try:
            # Process the payout through the service
            result = payout_service.process_payout(payout.id)
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully processed payout {payout.id} '
                        f'for driver {payout.driver.id}'
                    )
                )
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            # Revert status on failure
            with transaction.atomic():
                payout.status = DriverPayout.PayoutStatus.SCHEDULED
                payout.processed_date = None
                payout.save()
            raise e
    
    def _process_batch(self, batch, dry_run, payout_service):
        """Process a batch of payouts"""
        for payout in batch:
            try:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Would process payout {payout.id} '
                        f'for driver {payout.driver.id} '
                        f'amount: {payout.net_payout_amount} {payout.currency.code}'
                    )
                else:
                    self.process_single_payout(payout, payout_service)
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to process payout {payout.id}: {str(e)}'
                    )
                )
    
    def _payout_processed_successfully(self, payout):
        """Check if payout was processed successfully"""
        # Refresh from database to get latest status
        payout.refresh_from_db()
        return payout.status == DriverPayout.PayoutStatus.COMPLETED
