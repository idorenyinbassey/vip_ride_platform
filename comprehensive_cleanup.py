#!/usr/bin/env python3
"""
Comprehensive Cleanup Script for VIP Ride Platform
Performs final cleanup of unused test files, redundant scripts, and optimization
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict

class ComprehensiveCleanup:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.cleanup_report = {
            'timestamp': datetime.now().isoformat(),
            'files_removed': [],
            'directories_cleaned': [],
            'space_saved': 0,
            'errors': []
        }
    
    def cleanup_test_scripts(self):
        """Remove redundant test scripts that are no longer needed"""
        test_files_to_remove = [
            'test_flutter_integration.py',
            'test_flutter_http.py', 
            'test_flutter_activation.py',
            'test_gps_production_ready.py',
            'test_gps_direct.py',
            'test_gps_encryption_django.py',
            'test_gps_encryption_frontend.py',
            'test_gps_encryption_comprehensive.py',
            'test_improved_batch.py',
            'test_batch_generation.py'
        ]
        
        for filename in test_files_to_remove:
            file_path = self.root_path / filename
            if file_path.exists():
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    self.cleanup_report['files_removed'].append(str(file_path))
                    self.cleanup_report['space_saved'] += size
                    print(f"✅ Removed: {filename}")
                except Exception as e:
                    self.cleanup_report['errors'].append(f"Error removing {filename}: {str(e)}")
                    print(f"❌ Error removing {filename}: {e}")
    
    def cleanup_development_scripts(self):
        """Remove development and analysis scripts"""
        dev_scripts = [
            'advanced_cleanup.py',
            'enhanced_cleanup.py', 
            'quick_duplicate_analyzer.py',
            'create_test_rides.py',
            'create_test_users.py',
            'quick_gps_test.py'
        ]
        
        for filename in dev_scripts:
            file_path = self.root_path / filename
            if file_path.exists():
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    self.cleanup_report['files_removed'].append(str(file_path))
                    self.cleanup_report['space_saved'] += size
                    print(f"✅ Removed: {filename}")
                except Exception as e:
                    self.cleanup_report['errors'].append(f"Error removing {filename}: {str(e)}")
                    print(f"❌ Error removing {filename}: {e}")
    
    def cleanup_log_files(self):
        """Remove log files and temporary files"""
        patterns = ['*.log', '*.tmp', '*~', '*.bak']
        for pattern in patterns:
            for file_path in self.root_path.rglob(pattern):
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    self.cleanup_report['files_removed'].append(str(file_path))
                    self.cleanup_report['space_saved'] += size
                    print(f"✅ Removed: {file_path.name}")
                except Exception as e:
                    self.cleanup_report['errors'].append(f"Error removing {file_path}: {str(e)}")
    
    def cleanup_redundant_documentation(self):
        """Remove redundant or outdated documentation"""
        redundant_docs = [
            'DUPLICATE_CLEANUP_REPORT.md',  # Keep FINAL_CLEANUP_SUMMARY.md as it's more comprehensive
            'CLEANUP_REPORT.json',
            'duplicate_analysis_results.json'
        ]
        
        for filename in redundant_docs:
            file_path = self.root_path / filename
            if file_path.exists():
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    self.cleanup_report['files_removed'].append(str(file_path))
                    self.cleanup_report['space_saved'] += size
                    print(f"✅ Removed: {filename}")
                except Exception as e:
                    self.cleanup_report['errors'].append(f"Error removing {filename}: {str(e)}")
    
    def cleanup_old_backups(self):
        """Clean up old backup directories but keep the most recent one"""
        backup_dir = self.root_path / 'cleanup_backup'
        if backup_dir.exists():
            backup_folders = list(backup_dir.iterdir())
            if len(backup_folders) > 1:
                # Sort by creation time and keep only the most recent
                backup_folders.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for old_backup in backup_folders[1:]:  # Keep first (most recent), remove others
                    try:
                        shutil.rmtree(old_backup)
                        self.cleanup_report['directories_cleaned'].append(str(old_backup))
                        print(f"✅ Removed old backup: {old_backup.name}")
                    except Exception as e:
                        self.cleanup_report['errors'].append(f"Error removing {old_backup}: {str(e)}")
    
    def cleanup_mobile_build_artifacts(self):
        """Ensure mobile build artifacts are cleaned"""
        mobile_dir = self.root_path / 'mobile'
        if mobile_dir.exists():
            build_dirs = ['build', '.dart_tool']
            for dir_name in build_dirs:
                build_path = mobile_dir / dir_name
                if build_path.exists():
                    try:
                        shutil.rmtree(build_path)
                        self.cleanup_report['directories_cleaned'].append(str(build_path))
                        print(f"✅ Removed: {build_path}")
                    except Exception as e:
                        self.cleanup_report['errors'].append(f"Error removing {build_path}: {str(e)}")
    
    def optimize_imports(self):
        """Check for unused imports in Python files"""
        print("\n🔍 Checking for potential optimization opportunities...")
        
        python_files = list(self.root_path.rglob("*.py"))
        potential_issues = []
        
        for py_file in python_files:
            if any(skip in str(py_file) for skip in ['migrations', '__pycache__', 'cleanup_backup', '.venv', 'venv']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for common issues
                if 'import *' in content:
                    potential_issues.append(f"Star import found in {py_file}")
                    
                if content.count('TODO') > 0:
                    todo_count = content.count('TODO')
                    potential_issues.append(f"{todo_count} TODO items in {py_file}")
                    
            except Exception as e:
                pass
        
        if potential_issues:
            print("📝 Potential optimization opportunities found:")
            for issue in potential_issues[:10]:  # Show first 10
                print(f"  - {issue}")
    
    def generate_report(self):
        """Generate cleanup report"""
        report_path = self.root_path / 'COMPREHENSIVE_CLEANUP_REPORT.json'
        
        with open(report_path, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        print(f"\n📊 Cleanup Summary:")
        print(f"   Files removed: {len(self.cleanup_report['files_removed'])}")
        print(f"   Directories cleaned: {len(self.cleanup_report['directories_cleaned'])}")
        print(f"   Space saved: {self.cleanup_report['space_saved'] / 1024:.1f} KB")
        print(f"   Errors: {len(self.cleanup_report['errors'])}")
        print(f"   Report saved: {report_path}")
    
    def run_cleanup(self):
        """Execute the comprehensive cleanup"""
        print("🧹 Starting Comprehensive Cleanup...")
        print("=" * 50)
        
        self.cleanup_test_scripts()
        self.cleanup_development_scripts()
        self.cleanup_log_files()
        self.cleanup_redundant_documentation()
        self.cleanup_old_backups()
        self.cleanup_mobile_build_artifacts()
        self.optimize_imports()
        self.generate_report()
        
        print("\n✅ Comprehensive cleanup completed!")

if __name__ == "__main__":
    cleanup = ComprehensiveCleanup("/home/idorenyinbassey/My projects/workspace1/vip_ride_platforms")
    cleanup.run_cleanup()