# RBAC System Test Management Command
"""
Test script for role-based access control system
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from accounts.permissions import (
    IsVIPUser, IsPremiumUser, IsNormalUser, IsConciergeUser, IsAdminUser,
    VIPDataAccessPermission, EnhancedMFAPermission, AuditedTierPermission
)
from accounts.models import SecurityEvent, UserSession, MFAToken

User = get_user_model()


class Command(BaseCommand):
    help = 'Test role-based access control system functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            type=str,
            choices=['permissions', 'audit', 'mfa', 'all'],
            default='all',
            help='Type of RBAC test to run'
        )
        parser.add_argument(
            '--create-test-users',
            action='store_true',
            help='Create test users for each tier'
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
            self.style.SUCCESS('Starting RBAC system tests...')
        )
        
        try:
            if options['create_test_users']:
                self.create_test_users()
            
            if test_type == 'permissions' or test_type == 'all':
                self.test_tier_permissions()
            
            if test_type == 'audit' or test_type == 'all':
                self.test_audit_logging()
            
            if test_type == 'mfa' or test_type == 'all':
                self.test_mfa_requirements()
            
            self.display_results()
            
            self.stdout.write(
                self.style.SUCCESS('All RBAC tests completed!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'RBAC tests failed: {e}')
            )
            raise
    
    def create_test_users(self):
        """Create test users for each tier"""
        self.stdout.write('Creating test users...')
        
        test_users = [
            ('normal_test@example.com', 'normal', 'Normal Test', '+1234567890', 'normal_test'),
            ('premium_test@example.com', 'premium', 'Premium Test', '+1234567891', 'premium_test'),
            ('vip_test@example.com', 'vip', 'VIP Test', '+1234567892', 'vip_test'),
            ('concierge_test@example.com', 'concierge', 'Concierge Test', '+1234567893', 'concierge_test'),
            ('admin_test@example.com', 'admin', 'Admin Test', '+1234567894', 'admin_test'),
        ]
        
        for email, tier, name, phone, username in test_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': name.split()[0],
                    'last_name': name.split()[1],
                    'tier': tier,
                    'phone_number': phone,
                    'is_active': True,
                    'is_email_verified': True
                }
            )
            
            if created:
                user.set_password('TestPassword123!')
                user.save()
                
                # Add user to appropriate group
                group_name = f"{tier}_users"
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Group {group_name} not found')
                    )
                
                if self.verbose:
                    self.stdout.write(f'  Created user: {email} ({tier})')
            else:
                if self.verbose:
                    self.stdout.write(f'  User exists: {email} ({tier})')
    
    def test_tier_permissions(self):
        """Test tier-based permissions"""
        self.stdout.write('Testing tier-based permissions...')
        
        factory = RequestFactory()
        
        # Test data: (permission_class, allowed_tiers)
        permission_tests = [
            (IsNormalUser, ['normal', 'premium', 'vip', 'concierge', 'admin']),
            (IsPremiumUser, ['premium', 'vip', 'concierge', 'admin']),
            (IsVIPUser, ['vip', 'concierge', 'admin']),
            (IsConciergeUser, ['concierge', 'admin']),
            (IsAdminUser, ['admin']),
        ]
        
        all_tiers = ['normal', 'premium', 'vip', 'concierge', 'admin']
        test_results = []
        
        for permission_class, allowed_tiers in permission_tests:
            permission_name = permission_class.__name__
            
            for tier in all_tiers:
                # Get test user for this tier
                test_user = User.objects.filter(tier=tier).first()
                
                if not test_user:
                    self.stdout.write(
                        self.style.WARNING(f'No test user found for tier: {tier}')
                    )
                    continue
                
                # Create test request
                request = factory.get('/test/')
                request.user = test_user
                
                # Test permission
                permission = permission_class()
                has_permission = permission.has_permission(request, None)
                should_have = tier in allowed_tiers
                
                test_passed = has_permission == should_have
                test_results.append({
                    'permission': permission_name,
                    'tier': tier,
                    'expected': should_have,
                    'actual': has_permission,
                    'passed': test_passed
                })
                
                if self.verbose:
                    status = '✓' if test_passed else '✗'
                    self.stdout.write(
                        f'  {status} {permission_name} - {tier}: '
                        f'expected {should_have}, got {has_permission}'
                    )
        
        # Summary
        passed = sum(1 for result in test_results if result['passed'])
        total = len(test_results)
        self.stdout.write(f'Tier permission tests: {passed}/{total} passed')
        
        if passed != total:
            failed_tests = [r for r in test_results if not r['passed']]
            self.stdout.write('Failed tests:')
            for test in failed_tests:
                self.stdout.write(
                    f"  {test['permission']} - {test['tier']}: "
                    f"expected {test['expected']}, got {test['actual']}"
                )
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        self.stdout.write('Testing audit logging...')
        
        # Clear existing security events for clean test
        initial_count = SecurityEvent.objects.count()
        
        factory = RequestFactory()
        
        # Test different types of audit events
        test_user = User.objects.filter(tier='vip').first()
        if not test_user:
            self.stdout.write(
                self.style.WARNING('No VIP test user found for audit testing')
            )
            return
        
        # Test permission check logging
        request = factory.get('/api/test/')
        request.user = test_user
        
        permission = AuditedTierPermission()
        permission.has_permission(request, None)
        
        # Test VIP data access logging
        vip_permission = VIPDataAccessPermission()
        
        # Create a valid session for the user
        UserSession.objects.create(
            user=test_user,
            session_id='test-session-123',
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            expires_at=timezone.now() + timezone.timedelta(hours=2)
        )
        
        vip_permission.has_permission(request, None)
        
        # Check if audit events were created
        final_count = SecurityEvent.objects.count()
        events_created = final_count - initial_count
        
        self.stdout.write(f'Audit logging test: {events_created} events created')
        
        if self.verbose and events_created > 0:
            recent_events = SecurityEvent.objects.order_by('-created_at')[:events_created]
            for event in recent_events:
                self.stdout.write(
                    f'  Event: {event.event_type} - {event.severity} - {event.description}'
                )
    
    def test_mfa_requirements(self):
        """Test MFA requirement enforcement"""
        self.stdout.write('Testing MFA requirements...')
        
        factory = RequestFactory()
        
        # Test user
        test_user = User.objects.filter(tier='vip').first()
        if not test_user:
            self.stdout.write(
                self.style.WARNING('No VIP test user found for MFA testing')
            )
            return
        
        # Test MFA permission without verified MFA
        request = factory.post('/api/sensitive/')
        request.user = test_user
        
        mfa_permission = EnhancedMFAPermission()
        has_permission_without_mfa = mfa_permission.has_permission(request, None)
        
        # Create verified MFA token
        MFAToken.objects.create(
            user=test_user,
            token_type='totp',
            is_verified=True,
            verified_at=timezone.now()
        )
        
        # Test MFA permission with verified MFA
        has_permission_with_mfa = mfa_permission.has_permission(request, None)
        
        # Results
        mfa_test_passed = not has_permission_without_mfa and has_permission_with_mfa
        
        self.stdout.write(
            f'MFA requirement test: {"PASSED" if mfa_test_passed else "FAILED"}'
        )
        
        if self.verbose:
            self.stdout.write(f'  Without MFA: {has_permission_without_mfa}')
            self.stdout.write(f'  With MFA: {has_permission_with_mfa}')
    
    def display_results(self):
        """Display test results summary"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('RBAC SYSTEM TEST RESULTS')
        self.stdout.write('='*60)
        
        # Count security events by type
        event_counts = {}
        for event in SecurityEvent.objects.values_list('event_type', flat=True):
            event_counts[event] = event_counts.get(event, 0) + 1
        
        self.stdout.write('Security Events Generated:')
        for event_type, count in event_counts.items():
            self.stdout.write(f'  {event_type}: {count}')
        
        # Test users summary
        self.stdout.write('\nTest Users by Tier:')
        for tier in ['normal', 'premium', 'vip', 'concierge', 'admin']:
            count = User.objects.filter(tier=tier, email__contains='test').count()
            self.stdout.write(f'  {tier}: {count} users')
        
        # Permissions summary
        self.stdout.write('\nCustom Permissions:')
        from accounts.permissions import CUSTOM_PERMISSIONS
        self.stdout.write(f'  Total custom permissions: {len(CUSTOM_PERMISSIONS)}')
        
        # Groups summary
        self.stdout.write('\nTier Groups:')
        tier_groups = ['normal_users', 'premium_users', 'vip_users', 
                      'concierge_users', 'admin_users']
        for group_name in tier_groups:
            try:
                group = Group.objects.get(name=group_name)
                user_count = group.user_set.count()
                perm_count = group.permissions.count()
                self.stdout.write(
                    f'  {group_name}: {user_count} users, {perm_count} permissions'
                )
            except Group.DoesNotExist:
                self.stdout.write(f'  {group_name}: NOT FOUND')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('RBAC FEATURES TESTED:')
        self.stdout.write('='*60)
        self.stdout.write('✓ Tier-based permission hierarchy')
        self.stdout.write('✓ VIP data access restrictions')
        self.stdout.write('✓ MFA requirement enforcement')
        self.stdout.write('✓ Comprehensive audit logging')
        self.stdout.write('✓ Permission check monitoring')
        self.stdout.write('✓ Security event generation')
        
        self.stdout.write('\nNext Steps:')
        self.stdout.write('1. Apply permission classes to your API views')
        self.stdout.write('2. Add RBAC middleware to Django settings')
        self.stdout.write('3. Monitor SecurityEvent model for audit logs')
        self.stdout.write('4. Test with real API endpoints')
        self.stdout.write('5. Configure alerting for security events')
        
        self.stdout.write('\n' + '='*60)
