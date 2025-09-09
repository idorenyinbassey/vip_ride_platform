#!/usr/bin/env python3
"""
Django Test Runner for VIP Ride Platform
Run all tests using Django's built-in test framework
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vip_ride_platform.settings')
    
    # Set test database settings
    os.environ.setdefault('DEBUG', 'True')
    
    # Run tests
    execute_from_command_line(['manage.py', 'test'] + sys.argv[1:])
