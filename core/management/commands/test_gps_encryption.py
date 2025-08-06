# GPS Encryption Test Management Command
"""
Django management command to test GPS encryption system
"""

import time
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from core.encryption import GPSEncryptionManager
from core.gps_models import GPSEncryptionSession, EncryptedGPSData

User = get_user_model()


class Command(BaseCommand):
    help = 'Test GPS encryption system functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            type=str,
            choices=['basic', 'performance', 'concurrent', 'all'],
            default='basic',
            help='Type of test to run'
        )
        parser.add_argument(
            '--session-count',
            type=int,
            default=1,
            help='Number of encryption sessions to test'
        )
        parser.add_argument(
            '--data-points',
            type=int,
            default=10,
            help='Number of GPS data points per session'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        self.verbose = options['verbose']
        test_type = options['test_type']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting GPS encryption tests: {test_type}'
            )
        )
        
        try:
            if test_type == 'basic' or test_type == 'all':
                self.test_basic_encryption(options)
            
            if test_type == 'performance' or test_type == 'all':
                self.test_performance(options)
            
            if test_type == 'concurrent' or test_type == 'all':
                self.test_concurrent_sessions(options)
            
            self.stdout.write(
                self.style.SUCCESS('All GPS encryption tests completed!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Test failed with error: {e}')
            )
            raise
    
    def test_basic_encryption(self, options):
        """Test basic GPS encryption functionality"""
        self.stdout.write('Testing basic GPS encryption...')
        
        # Create test user if needed
        user, created = User.objects.get_or_create(
            email='gps_test@example.com',
            defaults={
                'first_name': 'GPS',
                'last_name': 'Test',
                'tier': 'vip',
                'is_active': True
            }
        )
        
        if created and self.verbose:
            self.stdout.write(f'Created test user: {user.email}')
        
        # Initialize encryption manager
        encryption_manager = GPSEncryptionManager()
        
        # Test key exchange
        ride_id = f'test-ride-{int(time.time())}'
        client_public_key = self._generate_test_public_key()
        
        session_result = encryption_manager.start_encryption_session(
            ride_id=ride_id,
            client_public_key=client_public_key
        )
        
        if not session_result['success']:
            raise Exception(f'Key exchange failed: {session_result["error"]}')
        
        session_id = session_result['session_id']
        if self.verbose:
            self.stdout.write(f'Session created: {session_id}')
        
        # Create session record
        expires_at = timezone.now() + timedelta(hours=2)
        gps_session = GPSEncryptionSession.objects.create(
            session_id=session_id,
            ride_id=ride_id,
            user=user,
            expires_at=expires_at,
            key_exchange_completed=True
        )
        
        # Test GPS data encryption
        test_coordinates = [
            {'latitude': 6.5244, 'longitude': 3.3792, 'timestamp': timezone.now()},
            {'latitude': 6.5245, 'longitude': 3.3793, 'timestamp': timezone.now()},
            {'latitude': 6.5246, 'longitude': 3.3794, 'timestamp': timezone.now()},
        ]
        
        encrypted_data_ids = []
        
        for i, coords in enumerate(test_coordinates):
            # Add some test metadata
            gps_data = {
                **coords,
                'speed': random.uniform(0, 60),
                'bearing': random.uniform(0, 360),
                'altitude': random.uniform(10, 100),
                'accuracy': random.uniform(1, 10)
            }
            
            # Encrypt GPS data
            encryption_result = encryption_manager.encrypt_gps_data(
                session_id=session_id,
                gps_data=gps_data
            )
            
            if not encryption_result['success']:
                raise Exception(
                    f'GPS encryption failed: {encryption_result["error"]}'
                )
            
            # Store encrypted data
            encrypted_gps = EncryptedGPSData.objects.create(
                session=gps_session,
                user=user,
                encrypted_data=encryption_result['encrypted_data'],
                nonce=encryption_result['nonce'],
                timestamp=gps_data['timestamp'],
                encrypted_speed=encryption_result.get('encrypted_speed', ''),
                encrypted_bearing=encryption_result.get('encrypted_bearing', ''),
                encrypted_altitude=encryption_result.get('encrypted_altitude', ''),
                encrypted_accuracy=encryption_result.get('encrypted_accuracy', '')
            )
            
            encrypted_data_ids.append(encrypted_gps.id)
            
            if self.verbose:
                self.stdout.write(
                    f'Encrypted GPS point {i+1}: '
                    f'{coords["latitude"]:.6f}, {coords["longitude"]:.6f}'
                )
        
        # Test GPS data decryption
        self.stdout.write('Testing GPS decryption...')
        
        for i, data_id in enumerate(encrypted_data_ids):
            encrypted_gps = EncryptedGPSData.objects.get(id=data_id)
            
            decryption_result = encryption_manager.decrypt_gps_data(
                session_id=session_id,
                encrypted_data=encrypted_gps.encrypted_data,
                nonce=encrypted_gps.nonce
            )
            
            if not decryption_result['success']:
                raise Exception(
                    f'GPS decryption failed: {decryption_result["error"]}'
                )
            
            decrypted_coords = decryption_result['gps_data']
            original_coords = test_coordinates[i]
            
            # Verify decrypted data matches original
            if (abs(decrypted_coords.latitude - original_coords['latitude']) > 0.000001 or
                abs(decrypted_coords.longitude - original_coords['longitude']) > 0.000001):
                raise Exception(
                    f'Decrypted coordinates do not match original: '
                    f'Expected {original_coords["latitude"]}, {original_coords["longitude"]} '
                    f'Got {decrypted_coords.latitude}, {decrypted_coords.longitude}'
                )
            
            if self.verbose:
                self.stdout.write(
                    f'Decrypted GPS point {i+1}: '
                    f'{decrypted_coords.latitude:.6f}, {decrypted_coords.longitude:.6f} ✓'
                )
        
        # Test session termination
        encryption_manager.end_encryption_session(session_id)
        gps_session.end_session()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Basic encryption test completed: {len(test_coordinates)} points encrypted/decrypted'
            )
        )
    
    def test_performance(self, options):
        """Test GPS encryption performance"""
        self.stdout.write('Testing GPS encryption performance...')
        
        data_points = options['data_points']
        
        # Create test user
        user, _ = User.objects.get_or_create(
            email='gps_perf_test@example.com',
            defaults={
                'first_name': 'GPS',
                'last_name': 'Performance',
                'tier': 'vip',
                'is_active': True
            }
        )
        
        # Initialize encryption manager
        encryption_manager = GPSEncryptionManager()
        
        # Start session
        ride_id = f'perf-test-{int(time.time())}'
        client_public_key = self._generate_test_public_key()
        
        session_result = encryption_manager.start_encryption_session(
            ride_id=ride_id,
            client_public_key=client_public_key
        )
        
        if not session_result['success']:
            raise Exception(f'Session creation failed: {session_result["error"]}')
        
        session_id = session_result['session_id']
        
        # Performance test data
        start_time = time.time()
        encryption_times = []
        decryption_times = []
        
        encrypted_data = []
        
        # Test encryption performance
        for i in range(data_points):
            gps_data = {
                'latitude': 6.5244 + (i * 0.0001),
                'longitude': 3.3792 + (i * 0.0001),
                'timestamp': timezone.now(),
                'speed': random.uniform(0, 60),
                'bearing': random.uniform(0, 360)
            }
            
            encrypt_start = time.time()
            result = encryption_manager.encrypt_gps_data(
                session_id=session_id,
                gps_data=gps_data
            )
            encrypt_time = (time.time() - encrypt_start) * 1000  # ms
            
            if not result['success']:
                raise Exception(f'Encryption failed: {result["error"]}')
            
            encryption_times.append(encrypt_time)
            encrypted_data.append({
                'encrypted_data': result['encrypted_data'],
                'nonce': result['nonce'],
                'original': gps_data
            })
        
        # Test decryption performance
        for data in encrypted_data:
            decrypt_start = time.time()
            result = encryption_manager.decrypt_gps_data(
                session_id=session_id,
                encrypted_data=data['encrypted_data'],
                nonce=data['nonce']
            )
            decrypt_time = (time.time() - decrypt_start) * 1000  # ms
            
            if not result['success']:
                raise Exception(f'Decryption failed: {result["error"]}')
            
            decryption_times.append(decrypt_time)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        avg_encrypt_time = sum(encryption_times) / len(encryption_times)
        avg_decrypt_time = sum(decryption_times) / len(decryption_times)
        max_encrypt_time = max(encryption_times)
        max_decrypt_time = max(decryption_times)
        
        throughput = data_points / total_time
        
        # Display results
        self.stdout.write(
            self.style.SUCCESS(
                f'Performance test results ({data_points} data points):'
            )
        )
        self.stdout.write(f'  Total time: {total_time:.2f}s')
        self.stdout.write(f'  Throughput: {throughput:.1f} points/second')
        self.stdout.write(f'  Avg encryption time: {avg_encrypt_time:.2f}ms')
        self.stdout.write(f'  Avg decryption time: {avg_decrypt_time:.2f}ms')
        self.stdout.write(f'  Max encryption time: {max_encrypt_time:.2f}ms')
        self.stdout.write(f'  Max decryption time: {max_decrypt_time:.2f}ms')
        
        # Check performance thresholds
        if avg_encrypt_time > 50:
            self.stdout.write(
                self.style.WARNING(
                    f'  WARNING: Average encryption time exceeds 50ms'
                )
            )
        
        if avg_decrypt_time > 50:
            self.stdout.write(
                self.style.WARNING(
                    f'  WARNING: Average decryption time exceeds 50ms'
                )
            )
        
        # Cleanup
        encryption_manager.end_encryption_session(session_id)
    
    def test_concurrent_sessions(self, options):
        """Test concurrent GPS encryption sessions"""
        self.stdout.write('Testing concurrent GPS encryption sessions...')
        
        session_count = options['session_count']
        
        # Create test users
        users = []
        for i in range(session_count):
            user, _ = User.objects.get_or_create(
                email=f'gps_concurrent_test_{i}@example.com',
                defaults={
                    'first_name': f'GPS{i}',
                    'last_name': 'Concurrent',
                    'tier': 'vip',
                    'is_active': True
                }
            )
            users.append(user)
        
        encryption_manager = GPSEncryptionManager()
        sessions = []
        
        # Create concurrent sessions
        start_time = time.time()
        
        for i, user in enumerate(users):
            ride_id = f'concurrent-test-{i}-{int(time.time())}'
            client_public_key = self._generate_test_public_key()
            
            session_result = encryption_manager.start_encryption_session(
                ride_id=ride_id,
                client_public_key=client_public_key
            )
            
            if not session_result['success']:
                raise Exception(
                    f'Session {i} creation failed: {session_result["error"]}'
                )
            
            sessions.append({
                'id': session_result['session_id'],
                'user': user,
                'ride_id': ride_id
            })
            
            if self.verbose:
                self.stdout.write(f'Created session {i+1}: {session_result["session_id"]}')
        
        # Test concurrent encryption
        for session in sessions:
            gps_data = {
                'latitude': 6.5244 + random.uniform(-0.01, 0.01),
                'longitude': 3.3792 + random.uniform(-0.01, 0.01),
                'timestamp': timezone.now(),
                'speed': random.uniform(0, 60)
            }
            
            result = encryption_manager.encrypt_gps_data(
                session_id=session['id'],
                gps_data=gps_data
            )
            
            if not result['success']:
                raise Exception(
                    f'Concurrent encryption failed for session {session["id"]}: '
                    f'{result["error"]}'
                )
        
        # Cleanup sessions
        for session in sessions:
            encryption_manager.end_encryption_session(session['id'])
        
        total_time = time.time() - start_time
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Concurrent sessions test completed: '
                f'{session_count} sessions in {total_time:.2f}s'
            )
        )
    
    def _generate_test_public_key(self):
        """Generate a test public key for ECDH"""
        # This is a simplified test key - in real implementation,
        # the client would generate proper ECDH keys
        import base64
        import os
        
        # Generate random bytes as test key
        test_key = os.urandom(32)
        return base64.b64encode(test_key).decode('utf-8')
    
    def _log_verbose(self, message):
        """Log verbose message if verbose mode is enabled"""
        if self.verbose:
            self.stdout.write(f'  {message}')
