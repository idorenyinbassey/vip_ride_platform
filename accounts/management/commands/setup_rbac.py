# Setup Role-Based Access Control Management Command
"""
Django management command to setup RBAC permissions and groups
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.permissions import (
    CUSTOM_PERMISSIONS,
    setup_tier_permissions,
    create_custom_permissions
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup role-based access control permissions and groups'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all permissions and groups before creating new ones'
        )
        parser.add_argument(
            '--assign-users',
            action='store_true',
            help='Assign existing users to their tier groups'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        self.verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('Setting up Role-Based Access Control system...')
        )
        
        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_permissions_and_groups()
                
                self.create_permissions()
                self.create_groups_and_assign_permissions()
                
                if options['assign_users']:
                    self.assign_users_to_groups()
                
                self.display_summary()
            
            self.stdout.write(
                self.style.SUCCESS('RBAC setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'RBAC setup failed: {e}')
            )
            raise
    
    def reset_permissions_and_groups(self):
        """Reset all custom permissions and tier groups"""
        self.stdout.write('Resetting existing permissions and groups...')
        
        # Delete tier groups
        tier_groups = ['normal_users', 'premium_users', 'vip_users', 
                      'concierge_users', 'admin_users']
        
        for group_name in tier_groups:
            try:
                group = Group.objects.get(name=group_name)
                group.delete()
                if self.verbose:
                    self.stdout.write(f'  Deleted group: {group_name}')
            except Group.DoesNotExist:
                pass
        
        # Delete custom permissions
        content_type = ContentType.objects.get_for_model(User)
        permission_codes = [perm[0] for perm in CUSTOM_PERMISSIONS]
        
        deleted_count = Permission.objects.filter(
            codename__in=permission_codes,
            content_type=content_type
        ).delete()[0]
        
        if self.verbose:
            self.stdout.write(f'  Deleted {deleted_count} custom permissions')
    
    def create_permissions(self):
        """Create custom permissions"""
        self.stdout.write('Creating custom permissions...')
        
        content_type = ContentType.objects.get_for_model(User)
        created_count = 0
        
        for codename, name in CUSTOM_PERMISSIONS:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            
            if created:
                created_count += 1
                if self.verbose:
                    self.stdout.write(f'  Created permission: {codename}')
        
        self.stdout.write(f'Created {created_count} new permissions')
    
    def create_groups_and_assign_permissions(self):
        """Create tier groups and assign permissions"""
        self.stdout.write('Creating tier groups and assigning permissions...')
        
        content_type = ContentType.objects.get_for_model(User)
        tier_permissions = setup_tier_permissions()
        
        for tier, permission_codes in tier_permissions.items():
            group, created = Group.objects.get_or_create(name=f"{tier}_users")
            
            if created and self.verbose:
                self.stdout.write(f'  Created group: {tier}_users')
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Add permissions
            assigned_count = 0
            for perm_code in permission_codes:
                try:
                    permission = Permission.objects.get(
                        codename=perm_code,
                        content_type=content_type
                    )
                    group.permissions.add(permission)
                    assigned_count += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Permission {perm_code} not found for tier {tier}'
                        )
                    )
            
            self.stdout.write(
                f'  Assigned {assigned_count} permissions to {tier}_users'
            )
    
    def assign_users_to_groups(self):
        """Assign existing users to their tier groups"""
        self.stdout.write('Assigning users to tier groups...')
        
        tier_groups = {
            'normal': Group.objects.get(name='normal_users'),
            'premium': Group.objects.get(name='premium_users'),
            'vip': Group.objects.get(name='vip_users'),
            'concierge': Group.objects.get(name='concierge_users'),
            'admin': Group.objects.get(name='admin_users'),
        }
        
        assigned_counts = {tier: 0 for tier in tier_groups.keys()}
        
        for user in User.objects.all():
            if user.tier in tier_groups:
                # Remove user from all tier groups first
                for group in tier_groups.values():
                    user.groups.remove(group)
                
                # Add to appropriate tier group
                tier_groups[user.tier].user_set.add(user)
                assigned_counts[user.tier] += 1
        
        for tier, count in assigned_counts.items():
            if count > 0:
                self.stdout.write(f'  Assigned {count} users to {tier}_users group')
    
    def display_summary(self):
        """Display summary of RBAC setup"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('ROLE-BASED ACCESS CONTROL SUMMARY')
        self.stdout.write('='*60)
        
        # Permissions summary
        content_type = ContentType.objects.get_for_model(User)
        total_permissions = Permission.objects.filter(
            content_type=content_type
        ).count()
        custom_permissions = Permission.objects.filter(
            codename__in=[perm[0] for perm in CUSTOM_PERMISSIONS],
            content_type=content_type
        ).count()
        
        self.stdout.write(f'Total Permissions: {total_permissions}')
        self.stdout.write(f'Custom Permissions: {custom_permissions}')
        
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
        
        # Permission breakdown by tier
        self.stdout.write('\nPermissions by Tier:')
        tier_permissions = setup_tier_permissions()
        
        for tier, permissions in tier_permissions.items():
            self.stdout.write(f'  {tier.upper()}:')
            for perm in permissions[:5]:  # Show first 5
                self.stdout.write(f'    - {perm}')
            if len(permissions) > 5:
                self.stdout.write(f'    ... and {len(permissions) - 5} more')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('RBAC System Features:')
        self.stdout.write('='*60)
        self.stdout.write('✓ Tier-based access control')
        self.stdout.write('✓ Custom Django permissions')
        self.stdout.write('✓ VIP data access restrictions')
        self.stdout.write('✓ MFA requirement enforcement')
        self.stdout.write('✓ Comprehensive audit logging')
        self.stdout.write('✓ API endpoint protection')
        self.stdout.write('✓ Operation-specific permissions')
        
        self.stdout.write('\nUsage Examples:')
        self.stdout.write('- Apply @permission_required("accounts.can_decrypt_gps") to views')
        self.stdout.write('- Use IsVIPUser permission class in DRF views')
        self.stdout.write('- Check user.has_perm("accounts.can_access_vip_data") in code')
        self.stdout.write('- Monitor SecurityEvent model for audit logs')
        
        self.stdout.write('\n' + '='*60)
