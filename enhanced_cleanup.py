#!/usr/bin/env python3
"""
Enhanced Duplicate and Empty File Cleanup Script for VIP Ride Platform
This script safely removes duplicate, empty, and redundant files while preserving critical functionality.
"""

import os
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

class SafeCleanupManager:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.files_to_remove: List[Path] = []
        self.files_to_backup: List[Path] = []
        self.backup_dir = self.root_path / 'cleanup_backup' / datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Critical files that should NEVER be removed (even if empty)
        self.critical_files = {
            'manage.py',
            'requirements.txt', 
            'runtime.txt',
            'Procfile',
            'Dockerfile',
            'docker-compose.yml',
            'settings.py',
            'urls.py',
            'wsgi.py',
            'asgi.py',
            '__init__.py'  # Django package init files
        }
        
        # Directories to completely skip
        self.skip_dirs = {
            '.git', '.venv', 'node_modules', '.dart_tool', 'build', 'dist',
            '.idea', '.vscode', '__pycache__', 'migrations', '.pytest_cache',
            'static', 'media', 'logs'
        }
        
        # Files that are known to be safe to remove (empty test/development files)
        self.safe_to_remove = {
            'consolidate_tests.py',
            'consolidate_hotels.py', 
            'consolidate_hotels_simple.py',
            'verify_consolidation.py',
            'check_users.py',
            'test_mfa_integration.py',
            'test_mfa_workflow.py',
            'test_tier_system.py',
            'test_totp_implementation.py',
            'totp_implementation_summary.py'
        }

    def should_skip_file(self, filepath: Path) -> bool:
        """Check if file should be skipped from cleanup"""
        # Skip if in skip directories
        for part in filepath.parts:
            if part in self.skip_dirs:
                return True
        
        # Skip if critical file
        if filepath.name in self.critical_files:
            return True
            
        # Skip if contains 'migration' in path (Django migrations)
        if 'migration' in str(filepath).lower():
            return True
            
        return False

    def is_empty_file(self, filepath: Path) -> bool:
        """Check if file is empty"""
        try:
            return filepath.stat().st_size == 0
        except OSError:
            return False

    def is_duplicate_file(self, filepath: Path, content_hashes: Dict[str, List[Path]]) -> bool:
        """Check if file is a duplicate based on content hash"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                if len(content) == 0:
                    return False  # Handle empty files separately
                file_hash = hashlib.md5(content).hexdigest()
                
                if file_hash in content_hashes:
                    # Check if this is a duplicate (not the original)
                    existing_files = content_hashes[file_hash]
                    if len(existing_files) > 0:
                        # Keep the file with the most "important" path
                        return self.is_less_important_duplicate(filepath, existing_files[0])
                else:
                    content_hashes[file_hash] = [filepath]
                return False
        except Exception:
            return False

    def is_less_important_duplicate(self, filepath: Path, existing_path: Path) -> bool:
        """Determine which duplicate file is less important"""
        # Prefer files in core/main directories over backup directories
        if 'backup' in str(filepath) and 'backup' not in str(existing_path):
            return True
        if 'old' in str(filepath) and 'old' not in str(existing_path):
            return True
        if '_new' in filepath.name and '_new' not in existing_path.name:
            return True
        if '_backup' in filepath.name and '_backup' not in existing_path.name:
            return True
        if '_clean' in filepath.name and '_clean' not in existing_path.name:
            return True
        return False

    def analyze_project(self):
        """Analyze project for cleanup opportunities"""
        print("🔍 Analyzing VIP Ride Platform for safe cleanup...")
        
        content_hashes: Dict[str, List[Path]] = {}
        
        for filepath in self.root_path.rglob('*'):
            if not filepath.is_file():
                continue
                
            if self.should_skip_file(filepath):
                continue
                
            # Check if it's a safe-to-remove development file
            if filepath.name in self.safe_to_remove:
                self.files_to_remove.append(filepath)
                print(f"📝 Marked for removal (development file): {filepath.relative_to(self.root_path)}")
                continue
                
            # Check for empty files (but not critical ones)
            if self.is_empty_file(filepath) and filepath.name not in self.critical_files:
                # Special handling for specific empty files
                if filepath.name == 'encryption.py' and 'gps_tracking' in str(filepath):
                    # This is the empty duplicate of core/encryption.py
                    self.files_to_remove.append(filepath)
                    print(f"📝 Marked for removal (empty duplicate): {filepath.relative_to(self.root_path)}")
                elif filepath.name.endswith('.py') and 'test' in filepath.name:
                    # Empty test files
                    self.files_to_remove.append(filepath)
                    print(f"📝 Marked for removal (empty test file): {filepath.relative_to(self.root_path)}")
                elif filepath.name.endswith('_new.py') or filepath.name.endswith('_backup.py'):
                    # Development backup files
                    self.files_to_remove.append(filepath)
                    print(f"📝 Marked for removal (dev backup): {filepath.relative_to(self.root_path)}")
                    
            # Check for duplicates
            if self.is_duplicate_file(filepath, content_hashes):
                self.files_to_remove.append(filepath)
                print(f"📝 Marked for removal (duplicate): {filepath.relative_to(self.root_path)}")

    def create_backup(self):
        """Create backup of files to be removed"""
        if not self.files_to_remove:
            return
            
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 Creating backup in: {self.backup_dir}")
        
        for filepath in self.files_to_remove:
            try:
                # Create backup path structure
                relative_path = filepath.relative_to(self.root_path)
                backup_path = self.backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file to backup
                shutil.copy2(filepath, backup_path)
                print(f"📦 Backed up: {relative_path}")
            except Exception as e:
                print(f"⚠️  Failed to backup {filepath}: {e}")

    def remove_files(self):
        """Remove files marked for cleanup"""
        if not self.files_to_remove:
            print("✅ No files to remove!")
            return
            
        print(f"\n🗑️  Removing {len(self.files_to_remove)} files...")
        removed_count = 0
        
        for filepath in self.files_to_remove:
            try:
                filepath.unlink()
                print(f"🗑️  Removed: {filepath.relative_to(self.root_path)}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {filepath}: {e}")
                
        print(f"\n✅ Successfully removed {removed_count} files!")
        
        if self.backup_dir.exists():
            print(f"📦 Backup created at: {self.backup_dir}")
            print(f"💡 To restore files: cp -r {self.backup_dir}/* {self.root_path}/")

    def generate_report(self):
        """Generate cleanup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_files_removed': len(self.files_to_remove),
            'backup_location': str(self.backup_dir) if self.backup_dir.exists() else None,
            'removed_files': [str(f.relative_to(self.root_path)) for f in self.files_to_remove]
        }
        
        report_file = self.root_path / 'CLEANUP_REPORT.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📄 Cleanup report saved to: {report_file}")

    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("🧹 VIP Ride Platform - Safe File Cleanup")
        print("=" * 50)
        
        self.analyze_project()
        
        if not self.files_to_remove:
            print("✅ No redundant files found! Project is clean.")
            return
            
        print(f"\n📋 Summary:")
        print(f"   Files to remove: {len(self.files_to_remove)}")
        
        # Show files to be removed
        print(f"\n📝 Files marked for removal:")
        for filepath in self.files_to_remove:
            print(f"   - {filepath.relative_to(self.root_path)}")
            
        response = input(f"\n🤔 Proceed with cleanup? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Cleanup cancelled.")
            return
            
        self.create_backup()
        self.remove_files()
        self.generate_report()
        
        print("\n🎉 Cleanup completed successfully!")
        print("💡 Run the project tests to ensure everything works correctly.")


if __name__ == "__main__":
    import sys
    
    # Get project root
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
        
    cleanup_manager = SafeCleanupManager(project_root)
    cleanup_manager.run_cleanup()
