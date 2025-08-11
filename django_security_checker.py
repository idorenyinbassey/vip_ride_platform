#!/usr/bin/env python3
"""
Django Security Configuration Checker
=====================================

This script checks Django settings and configurations for common security issues.
It analyzes the Django project structure and settings for security best practices.
"""

import os
import re
import sys
from pathlib import Path

class DjangoSecurityChecker:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.settings_path = None
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def find_settings_file(self):
        """Find Django settings file using directory tree walk"""
        # First try common hard-coded paths for better performance
        common_paths = [
            self.project_path / "settings.py",
            self.project_path / "vip_ride_platform" / "settings.py",
            self.project_path / "config" / "settings.py"
        ]
        
        for path in common_paths:
            if path.exists():
                self.settings_path = path
                return True
        
        # If not found, walk the directory tree to find any settings.py
        for root, dirs, files in os.walk(self.project_path):
            # Skip common directories that shouldn't contain settings
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', '.pytest_cache', 'node_modules',
                '.venv', 'venv', 'env', '.env', 'static', 'media'
            }]
            
            if 'settings.py' in files:
                settings_path = Path(root) / 'settings.py'
                # Verify it's a Django settings file by checking for common settings
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if any(setting in content for setting in [
                            'DJANGO_SETTINGS_MODULE', 'SECRET_KEY', 'INSTALLED_APPS'
                        ]):
                            self.settings_path = settings_path
                            return True
                except (IOError, UnicodeDecodeError):
                    continue
        
        return False
    
    def read_settings(self):
        """Read Django settings file"""
        if not self.settings_path:
            return None
            
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading settings file: {e}")
            return None
    
    def check_debug_setting(self, settings_content):
        """Check DEBUG setting"""
        if re.search(r'DEBUG\s*=\s*True', settings_content):
            self.issues.append({
                'category': 'Critical',
                'issue': 'DEBUG = True in production',
                'description': 'Debug mode should be disabled in production',
                'recommendation': 'Set DEBUG = False'
            })
        else:
            self.passed.append('DEBUG setting properly configured')
    
    def check_secret_key(self, settings_content):
        """Check SECRET_KEY configuration"""
        # Check for hardcoded secret key
        secret_key_match = re.search(r'SECRET_KEY\s*=\s*[\'"]([^\'"]+)[\'"]', settings_content)
        if secret_key_match:
            secret_key = secret_key_match.group(1)
            if 'django-insecure' in secret_key:
                self.warnings.append({
                    'category': 'Warning',
                    'issue': 'Default Django secret key detected',
                    'description': 'Using default Django secret key',
                    'recommendation': 'Generate a new SECRET_KEY'
                })
            elif len(secret_key) < 50:
                self.warnings.append({
                    'category': 'Warning',
                    'issue': 'Short SECRET_KEY',
                    'description': 'SECRET_KEY should be at least 50 characters',
                    'recommendation': 'Use a longer, more secure SECRET_KEY'
                })
        
        # Check if SECRET_KEY is loaded from environment
        if 'os.environ.get' in settings_content and 'SECRET_KEY' in settings_content:
            self.passed.append('SECRET_KEY loaded from environment variable')
    
    def check_allowed_hosts(self, settings_content):
        """Check ALLOWED_HOSTS configuration"""
        if re.search(r'ALLOWED_HOSTS\s*=\s*\[\s*\]', settings_content):
            self.issues.append({
                'category': 'High',
                'issue': 'Empty ALLOWED_HOSTS',
                'description': 'ALLOWED_HOSTS should be configured for production',
                'recommendation': 'Add your domain to ALLOWED_HOSTS'
            })
        elif '*' in settings_content and 'ALLOWED_HOSTS' in settings_content:
            self.warnings.append({
                'category': 'Warning',
                'issue': 'Wildcard in ALLOWED_HOSTS',
                'description': 'Using wildcard (*) in ALLOWED_HOSTS can be insecure',
                'recommendation': 'Specify exact domains instead of wildcards'
            })
        else:
            self.passed.append('ALLOWED_HOSTS properly configured')
    
    def check_database_security(self, settings_content):
        """Check database security settings"""
        # Check for hardcoded database credentials
        if re.search(r'[\'"]PASSWORD[\'"]:\s*[\'"][^\'"]+[\'"]', settings_content):
            self.issues.append({
                'category': 'Critical',
                'issue': 'Hardcoded database password',
                'description': 'Database password is hardcoded in settings',
                'recommendation': 'Use environment variables for database credentials'
            })
        
        # Check for SQLite in production
        if 'sqlite3' in settings_content:
            self.warnings.append({
                'category': 'Warning',
                'issue': 'SQLite database detected',
                'description': 'SQLite may not be suitable for production',
                'recommendation': 'Consider PostgreSQL or MySQL for production'
            })
    
    def check_security_middleware(self, settings_content):
        """Check security middleware configuration"""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware'
        ]
        
        for middleware in required_middleware:
            if middleware not in settings_content:
                self.warnings.append({
                    'category': 'Warning',
                    'issue': f'Missing {middleware}',
                    'description': f'Security middleware {middleware} not found',
                    'recommendation': f'Add {middleware} to MIDDLEWARE'
                })
            else:
                self.passed.append(f'{middleware} properly configured')
    
    def check_https_settings(self, settings_content):
        """Check HTTPS security settings"""
        https_settings = {
            'SECURE_SSL_REDIRECT': 'Force HTTPS redirects',
            'SECURE_HSTS_SECONDS': 'HTTP Strict Transport Security',
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': 'HSTS for subdomains',
            'SECURE_CONTENT_TYPE_NOSNIFF': 'Content type sniffing protection',
            'SECURE_BROWSER_XSS_FILTER': 'XSS filter protection',
            'SECURE_HSTS_PRELOAD': 'HSTS preload'
        }
        
        for setting, description in https_settings.items():
            if setting not in settings_content:
                self.warnings.append({
                    'category': 'Warning',
                    'issue': f'Missing {setting}',
                    'description': f'HTTPS security setting missing: {description}',
                    'recommendation': f'Add {setting} = True for production'
                })
    
    def check_session_security(self, settings_content):
        """Check session security settings"""
        session_settings = {
            'SESSION_COOKIE_SECURE': 'Secure session cookies',
            'SESSION_COOKIE_HTTPONLY': 'HTTP-only session cookies',
            'CSRF_COOKIE_SECURE': 'Secure CSRF cookies',
            'CSRF_COOKIE_HTTPONLY': 'HTTP-only CSRF cookies'
        }
        
        for setting, description in session_settings.items():
            if f'{setting} = True' not in settings_content:
                self.warnings.append({
                    'category': 'Warning',
                    'issue': f'Insecure {setting}',
                    'description': f'Cookie security setting: {description}',
                    'recommendation': f'Set {setting} = True'
                })
    
    def check_password_validation(self, settings_content):
        """Check password validation settings"""
        validators = [
            'UserAttributeSimilarityValidator',
            'MinimumLengthValidator',
            'CommonPasswordValidator',
            'NumericPasswordValidator'
        ]
        
        missing_validators = []
        for validator in validators:
            if validator not in settings_content:
                missing_validators.append(validator)
        
        if missing_validators:
            self.warnings.append({
                'category': 'Warning',
                'issue': 'Weak password validation',
                'description': f'Missing password validators: {", ".join(missing_validators)}',
                'recommendation': 'Enable all Django password validators'
            })
        else:
            self.passed.append('Password validation properly configured')
    
    def check_cors_configuration(self, settings_content):
        """Check CORS configuration if present"""
        if 'CORS_ALLOW_ALL_ORIGINS' in settings_content:
            if 'CORS_ALLOW_ALL_ORIGINS = True' in settings_content:
                self.issues.append({
                    'category': 'High',
                    'issue': 'CORS allows all origins',
                    'description': 'CORS_ALLOW_ALL_ORIGINS = True is insecure',
                    'recommendation': 'Use CORS_ALLOWED_ORIGINS with specific domains'
                })
        
        if 'CORS_ALLOW_CREDENTIALS = True' in settings_content:
            self.warnings.append({
                'category': 'Warning',
                'issue': 'CORS allows credentials',
                'description': 'CORS_ALLOW_CREDENTIALS = True requires careful configuration',
                'recommendation': 'Ensure CORS_ALLOWED_ORIGINS is properly configured'
            })
    
    def check_file_permissions(self):
        """Check file and directory permissions"""
        sensitive_files = [
            self.settings_path,
            self.project_path / "manage.py",
            self.project_path / ".env"
        ]
        
        for file_path in sensitive_files:
            if file_path.exists():
                try:
                    stat_info = file_path.stat()
                    # Check if file is world-readable (permissions & 0o004)
                    if stat_info.st_mode & 0o004:
                        self.warnings.append({
                            'category': 'Warning',
                            'issue': f'World-readable file: {file_path.name}',
                            'description': f'File {file_path} is readable by others',
                            'recommendation': 'Change file permissions to restrict access'
                        })
                except Exception:
                    pass  # Skip if we can't check permissions
    
    def check_environment_variables(self):
        """Check for .env file and environment variable usage"""
        env_file = self.project_path / ".env"
        if env_file.exists():
            self.passed.append('.env file found for configuration')
            
            try:
                with open(env_file, 'r') as f:
                    env_content = f.read()
                    
                # Check for sensitive data in .env
                if 'SECRET_KEY' in env_content:
                    self.passed.append('SECRET_KEY stored in environment file')
                
                if 'DATABASE_PASSWORD' in env_content or 'DB_PASSWORD' in env_content:
                    self.passed.append('Database password stored in environment file')
                    
            except Exception:
                pass
        else:
            self.warnings.append({
                'category': 'Warning',
                'issue': 'No .env file found',
                'description': 'Consider using .env file for sensitive configuration',
                'recommendation': 'Create .env file for environment-specific settings'
            })
    
    def run_all_checks(self):
        """Run all security checks"""
        print("🔒 Django Security Configuration Checker")
        print("=" * 50)
        
        if not self.find_settings_file():
            print("❌ Django settings file not found!")
            return False
        
        print(f"📁 Checking: {self.settings_path}")
        
        settings_content = self.read_settings()
        if not settings_content:
            print("❌ Could not read settings file!")
            return False
        
        # Run all checks
        self.check_debug_setting(settings_content)
        self.check_secret_key(settings_content)
        self.check_allowed_hosts(settings_content)
        self.check_database_security(settings_content)
        self.check_security_middleware(settings_content)
        self.check_https_settings(settings_content)
        self.check_session_security(settings_content)
        self.check_password_validation(settings_content)
        self.check_cors_configuration(settings_content)
        self.check_file_permissions()
        self.check_environment_variables()
        
        return True
    
    def generate_report(self):
        """Generate security report"""
        print("\n" + "=" * 50)
        print("📊 SECURITY CONFIGURATION REPORT")
        print("=" * 50)
        
        # Critical Issues
        critical_issues = [i for i in self.issues if i['category'] == 'Critical']
        if critical_issues:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"  ❌ {issue['issue']}")
                print(f"     {issue['description']}")
                print(f"     → {issue['recommendation']}")
                print()
        
        # High Priority Issues
        high_issues = [i for i in self.issues if i['category'] == 'High']
        if high_issues:
            print("🔴 HIGH PRIORITY ISSUES:")
            for issue in high_issues:
                print(f"  ❌ {issue['issue']}")
                print(f"     {issue['description']}")
                print(f"     → {issue['recommendation']}")
                print()
        
        # Warnings
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning['issue']}")
                print(f"     {warning['description']}")
                print(f"     → {warning['recommendation']}")
                print()
        
        # Passed Checks
        if self.passed:
            print("✅ PASSED CHECKS:")
            for check in self.passed:
                print(f"  ✅ {check}")
            print()
        
        # Summary
        total_issues = len(self.issues) + len(self.warnings)
        print(f"📈 SUMMARY:")
        print(f"  Critical Issues: {len(critical_issues)}")
        print(f"  High Issues: {len(high_issues)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Passed: {len(self.passed)}")
        print(f"  Total Issues: {total_issues}")
        
        # Security Score
        if len(self.passed) + total_issues > 0:
            score = (len(self.passed) / (len(self.passed) + total_issues)) * 100
            print(f"  Security Score: {score:.1f}/100")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Django Security Configuration Checker')
    parser.add_argument('project_path', nargs='?', default=os.getcwd(),
                       help='Path to Django project directory')
    parser.add_argument('--settings-path', 
                       help='Exact path to Django settings.py file')
    
    args = parser.parse_args()
    
    checker = DjangoSecurityChecker(args.project_path)
    
    # Override settings path if provided
    if args.settings_path:
        settings_path = Path(args.settings_path)
        if settings_path.exists():
            checker.settings_path = settings_path
        else:
            print(f"❌ Settings file not found: {args.settings_path}")
            return
    
    if checker.run_all_checks():
        checker.generate_report()
    else:
        print("❌ Security check failed to run")

if __name__ == "__main__":
    main()
