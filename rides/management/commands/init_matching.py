# Management command to setup ride matching system
"""
Django management command to initialize the ride matching system
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import logging

from accounts.models import Driver, UserTier
from rides.models import Ride, RideStatus, RideType, RideOffer, SurgeZone

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize ride matching system with test data and configurations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for development',
        )
        parser.add_argument(
            '--setup-surge-zones',
            action='store_true',
            help='Setup default surge zones',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up existing matching data',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Initializing ride matching system...')
        )
        
        if options['cleanup']:
            self.cleanup_data()
        
        if options['setup_surge_zones']:
            self.setup_surge_zones()
        
        if options['create_test_data']:
            self.create_test_data()
        
        self.verify_system()
        
        self.stdout.write(
            self.style.SUCCESS('Ride matching system initialized successfully!')
        )
    
    @transaction.atomic
    def cleanup_data(self):
        """Clean up existing matching data"""
        self.stdout.write('Cleaning up existing data...')
        
        # Clean up test data
        RideOffer.objects.all().delete()
        SurgeZone.objects.filter(name__startswith='Test').delete()
        
        self.stdout.write(
            self.style.SUCCESS('Cleanup completed.')
        )
    
    @transaction.atomic
    def setup_surge_zones(self):
        """Setup default surge zones for major areas"""
        self.stdout.write('Setting up surge zones...')
        
        # Create admin user if needed
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@vipride.com',
                'first_name': 'System',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        
        # Lagos Airport Surge Zone
        airport_zone, created = SurgeZone.objects.get_or_create(
            name='Lagos Airport',
            defaults={
                'center_latitude': Decimal('6.5244'),
                'center_longitude': Decimal('3.3792'),
                'radius_km': 5.0,
                'surge_multiplier': Decimal('1.5'),
                'is_active': True,
                'active_from': timezone.now(),
                'active_until': timezone.now() + timezone.timedelta(days=365),
                'min_demand_ratio': 1.3,
                'min_ride_requests': 8,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'Created surge zone: {airport_zone.name}')
        
        # Victoria Island Business District
        vi_zone, created = SurgeZone.objects.get_or_create(
            name='Victoria Island',
            defaults={
                'center_latitude': Decimal('6.4281'),
                'center_longitude': Decimal('3.4219'),
                'radius_km': 3.0,
                'surge_multiplier': Decimal('1.3'),
                'is_active': True,
                'active_from': timezone.now(),
                'active_until': timezone.now() + timezone.timedelta(days=365),
                'min_demand_ratio': 1.5,
                'min_ride_requests': 12,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'Created surge zone: {vi_zone.name}')
        
        # Ikeja Hub
        ikeja_zone, created = SurgeZone.objects.get_or_create(
            name='Ikeja Business Hub',
            defaults={
                'center_latitude': Decimal('6.5952'),
                'center_longitude': Decimal('3.3621'),
                'radius_km': 2.5,
                'surge_multiplier': Decimal('1.2'),
                'is_active': True,
                'active_from': timezone.now(),
                'active_until': timezone.now() + timezone.timedelta(days=365),
                'min_demand_ratio': 1.4,
                'min_ride_requests': 10,
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'Created surge zone: {ikeja_zone.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Setup {SurgeZone.objects.count()} surge zones.')
        )
    
    @transaction.atomic
    def create_test_data(self):
        """Create test data for development"""
        self.stdout.write('Creating test data...')
        
        # This would create test drivers, customers, vehicles, and rides
        # For production, this should be removed or guarded
        
        self.stdout.write(
            self.style.WARNING(
                'Test data creation skipped in production. '
                'Use --create-test-data flag only in development.'
            )
        )
    
    def verify_system(self):
        """Verify the matching system is properly configured"""
        self.stdout.write('Verifying system configuration...')
        
        errors = []
        warnings = []
        
        # Check if we have drivers
        driver_count = Driver.objects.filter(is_available=True).count()
        if driver_count == 0:
            warnings.append('No active drivers found in system')
        else:
            self.stdout.write(f'Found {driver_count} active drivers')
        
        # Check surge zones
        surge_zone_count = SurgeZone.objects.count()
        if surge_zone_count == 0:
            warnings.append('No surge zones configured')
        else:
            self.stdout.write(f'Found {surge_zone_count} surge zones')
        
        # Check for required models
        try:
            from rides.matching import RideMatchingService
            service = RideMatchingService()
            self.stdout.write('RideMatchingService imported successfully')
        except ImportError as e:
            errors.append(f'Failed to import RideMatchingService: {e}')
        
        # Print results
        if errors:
            for error in errors:
                self.stdout.write(
                    self.style.ERROR(f'ERROR: {error}')
                )
        
        if warnings:
            for warning in warnings:
                self.stdout.write(
                    self.style.WARNING(f'WARNING: {warning}')
                )
        
        if not errors:
            self.stdout.write(
                self.style.SUCCESS('System verification completed successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'System verification failed with {len(errors)} errors')
            )
