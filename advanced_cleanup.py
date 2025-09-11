#!/usr/bin/env python3
"""
Advanced Cleanup Script for VIP Ride Platform
Removes redundant documentation, old scripts, and unused analysis files
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Set

class AdvancedCleanup:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        
        # Redundant analysis and cleanup files
        self.redundant_analysis_files = {
            'analyze_duplicates.py',  # Keep quick_duplicate_analyzer.py as it's more recent
            'cleanup_duplicates.sh',  # Keep safe_cleanup.sh as it's more comprehensive
            'final_cleanup.sh',       # Old cleanup script
            'run_tests.py',          # Use Django's manage.py test instead
        }
        
        # Old documentation that's been consolidated
        self.redundant_docs = {
            'ARCHITECTURE_SUMMARY.md',      # Consolidated into main docs
            'CLEANUP_SUMMARY.md',           # Already have DUPLICATE_CLEANUP_REPORT.md
            'DEVELOPMENT_CONFIGURATION_GUIDE.md',  # Consolidated
            'DEVELOPMENT_MILESTONE_SUMMARY.md',    # Project specific, keep
            'DUPLICATE_CLEANUP_REPORT.md',         # Keep as recent
            'IMPLEMENTATION_GAP_ANALYSIS.md',      # Keep as useful
            'IMPROVEMENTS_SUMMARY.md',             # Keep as useful
            'METRICS_ENDPOINT_FIX.md',             # Keep as specific fix
            'MONITORING_INTEGRATION_COMPLETE.md',  # Keep as completion record
            'TEST_CLEANUP_SUMMARY.md',            # Remove, redundant
            'TIER_NAMING_FIX_SUMMARY.md',         # Keep as specific fix
            'TOTP_IMPLEMENTATION_COMPLETE.md',    # Keep as completion record
            'VIP_PREMIUM_IMPLEMENTATION_COMPLETE.md',  # Keep as completion record
        }
        
        # Analysis result files that can be cleaned up
        self.analysis_results = {
            'duplicate_analysis_results.json',  # Keep most recent analysis
            'manual_cleanup_recommendations.txt',  # Can remove after implementing
        }

    def get_files_to_remove(self) -> List[Path]:
        """Get list of files that can be safely removed"""
        files_to_remove = []
        
        # Check for redundant analysis files
        for filename in self.redundant_analysis_files:
            filepath = self.root_path / filename
            if filepath.exists():
                files_to_remove.append(filepath)
                
        # Check for redundant docs (be selective)
        redundant_docs_to_remove = {
            'CLEANUP_SUMMARY.md',      # We have DUPLICATE_CLEANUP_REPORT.md
            'TEST_CLEANUP_SUMMARY.md', # Redundant test summary
        }
        
        for filename in redundant_docs_to_remove:
            filepath = self.root_path / filename
            if filepath.exists():
                files_to_remove.append(filepath)
                
        # Check for old analysis results (keep the most recent)
        manual_recommendations = self.root_path / 'manual_cleanup_recommendations.txt'
        if manual_recommendations.exists():
            files_to_remove.append(manual_recommendations)
            
        return files_to_remove

    def clean_mobile_generated_files(self) -> List[Path]:
        """Clean up Flutter/Dart generated files that can be regenerated"""
        files_to_remove = []
        mobile_dir = self.root_path / 'mobile'
        
        if not mobile_dir.exists():
            return files_to_remove
            
        # Flutter generated files that can be safely removed
        generated_patterns = [
            '.dart_tool/**',
            '.flutter-plugins',
            '.flutter-plugins-dependencies', 
            'build/**',
            '.packages',
            'pubspec.lock'  # Can be regenerated with pub get
        ]
        
        for pattern in generated_patterns:
            for filepath in mobile_dir.glob(pattern):
                if filepath.is_file():
                    files_to_remove.append(filepath)
                    
        return files_to_remove

    def run_advanced_cleanup(self):
        """Run the advanced cleanup process"""
        print("🧹 Advanced Cleanup - VIP Ride Platform")
        print("=" * 50)
        
        files_to_remove = self.get_files_to_remove()
        mobile_files = self.clean_mobile_generated_files()
        
        all_files = files_to_remove + mobile_files
        
        if not all_files:
            print("✅ No additional redundant files found!")
            return
            
        print(f"📋 Found {len(all_files)} additional files to clean up:")
        print("\n📝 Redundant files:")
        for filepath in files_to_remove:
            print(f"   - {filepath.relative_to(self.root_path)}")
            
        if mobile_files:
            print(f"\n📱 Mobile generated files (can be regenerated):")
            for filepath in mobile_files:
                print(f"   - {filepath.relative_to(self.root_path)}")
                
        response = input(f"\n🤔 Remove these {len(all_files)} files? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Advanced cleanup cancelled.")
            return
            
        # Create backup
        backup_dir = self.root_path / 'cleanup_backup' / datetime.now().strftime('%Y%m%d_%H%M%S_advanced')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        removed_count = 0
        for filepath in all_files:
            try:
                # Backup first
                relative_path = filepath.relative_to(self.root_path)
                backup_path = backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                if filepath.is_file():
                    shutil.copy2(filepath, backup_path)
                    filepath.unlink()
                    print(f"🗑️  Removed: {relative_path}")
                    removed_count += 1
                elif filepath.is_dir():
                    shutil.copytree(filepath, backup_path, dirs_exist_ok=True)
                    shutil.rmtree(filepath)
                    print(f"🗑️  Removed directory: {relative_path}")
                    removed_count += 1
                    
            except Exception as e:
                print(f"❌ Failed to remove {filepath}: {e}")
                
        print(f"\n✅ Advanced cleanup completed! Removed {removed_count} files/directories.")
        print(f"📦 Backup created at: {backup_dir}")

if __name__ == "__main__":
    import sys
    
    # Get project root
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
        
    cleanup = AdvancedCleanup(project_root)
    cleanup.run_advanced_cleanup()
