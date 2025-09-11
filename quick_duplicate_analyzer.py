#!/usr/bin/env python3
"""
Quick Duplicate File Analyzer - Fast version with progress updates
Identifies duplicate and empty files in the VIP Ride Platform codebase
"""

import os
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import time

def get_file_hash(filepath):
    """Get MD5 hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            if len(content) == 0:
                return "EMPTY_FILE"
            return hashlib.md5(content).hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def is_important_file(filepath):
    """Check if file should be analyzed (skip binary, cache, etc.)"""
    skip_dirs = {
        '__pycache__', '.git', 'node_modules', '.vscode', 
        'migrations', '.pytest_cache', 'build', 'dist',
        'flutter', 'android', 'ios', 'web', 'windows', 'linux', 'macos'
    }
    
    skip_extensions = {
        '.pyc', '.pyo', '.log', '.tmp', '.cache', '.lock',
        '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
        '.ttf', '.otf', '.woff', '.woff2', '.so', '.dll', '.exe'
    }
    
    filepath_str = str(filepath)
    
    # Skip if in skip directories
    for skip_dir in skip_dirs:
        if f'/{skip_dir}/' in filepath_str or filepath_str.endswith(f'/{skip_dir}'):
            return False
    
    # Skip if has skip extensions
    if filepath.suffix.lower() in skip_extensions:
        return False
        
    return True

def analyze_project():
    """Quick analysis of the project"""
    project_root = Path('/home/idorenyinbassey/My projects/workspace1/vip_ride_platform')
    
    print("🔍 Quick Duplicate File Analysis")
    print("=" * 50)
    
    # Track files by hash
    file_hashes = defaultdict(list)
    empty_files = []
    total_files = 0
    analyzed_files = 0
    
    # Quick scan for Python files first
    print("\n📁 Analyzing Python files...")
    for py_file in project_root.rglob('*.py'):
        if not is_important_file(py_file):
            continue
            
        total_files += 1
        file_hash = get_file_hash(py_file)
        
        if file_hash == "EMPTY_FILE":
            empty_files.append(str(py_file))
        elif file_hash:
            file_hashes[file_hash].append(str(py_file))
            analyzed_files += 1
            
        if total_files % 10 == 0:
            print(f"  Processed {total_files} Python files...", end='\r')
    
    print(f"\n  ✅ Analyzed {analyzed_files} Python files")
    
    # Quick scan for other important files
    print("\n📄 Analyzing other files (Dart, JS, config files)...")
    other_patterns = ['*.dart', '*.js', '*.json', '*.yaml', '*.yml', '*.md', '*.txt', '*.sh', '*.sql']
    
    for pattern in other_patterns:
        for file_path in project_root.rglob(pattern):
            if not is_important_file(file_path):
                continue
                
            total_files += 1
            file_hash = get_file_hash(file_path)
            
            if file_hash == "EMPTY_FILE":
                empty_files.append(str(file_path))
            elif file_hash:
                file_hashes[file_hash].append(str(file_path))
                analyzed_files += 1
    
    print(f"  ✅ Total analyzed: {analyzed_files} files")
    
    # Find duplicates
    duplicates = {hash_val: files for hash_val, files in file_hashes.items() if len(files) > 1}
    
    # Report results
    print("\n" + "=" * 50)
    print("📊 ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"📈 Total files processed: {total_files}")
    print(f"📈 Files analyzed: {analyzed_files}")
    print(f"🗑️ Empty files found: {len(empty_files)}")
    print(f"🔄 Duplicate groups found: {len(duplicates)}")
    
    # Show empty files
    if empty_files:
        print("\n🗑️ EMPTY FILES TO DELETE:")
        print("-" * 30)
        for empty_file in sorted(empty_files):
            rel_path = os.path.relpath(empty_file, project_root)
            print(f"  ❌ {rel_path}")
    
    # Show duplicates
    if duplicates:
        print(f"\n🔄 DUPLICATE FILES ({len(duplicates)} groups):")
        print("-" * 40)
        
        for i, (hash_val, files) in enumerate(duplicates.items(), 1):
            print(f"\n📋 Group {i} ({len(files)} files):")
            for file_path in sorted(files):
                rel_path = os.path.relpath(file_path, project_root)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                print(f"  🔸 {rel_path} ({file_size} bytes)")
    
    # Quick analysis of known problem files
    print("\n🎯 KNOWN ISSUES ANALYSIS:")
    print("-" * 30)
    
    known_duplicates = [
        ('pricing/models.py', 'pricing/models_new.py', 'pricing/models_simple.py'),
        ('core/encryption.py', 'gps_tracking/encryption.py'),
        ('accounts/payment_service.py', 'accounts/payment_service_new.py'),
        ('vip_ride_platform/api_views.py', 'vip_ride_platform/api_views_new.py')
    ]
    
    for group in known_duplicates:
        existing = []
        for file_path in group:
            full_path = project_root / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                existing.append(f"{file_path} ({size} bytes)")
        
        if len(existing) > 1:
            print(f"  🔄 {' vs '.join(existing)}")
    
    # Generate cleanup script
    cleanup_script = generate_cleanup_script(empty_files, duplicates, project_root)
    
    return {
        'empty_files': empty_files,
        'duplicates': duplicates,
        'total_files': total_files,
        'analyzed_files': analyzed_files,
        'cleanup_script': cleanup_script
    }

def generate_cleanup_script(empty_files, duplicates, project_root):
    """Generate a script to clean up duplicate and empty files"""
    script_lines = [
        "#!/bin/bash",
        "# Auto-generated cleanup script for VIP Ride Platform",
        "# Run with: bash cleanup_duplicates.sh",
        "",
        "echo '🧹 Cleaning up duplicate and empty files...'",
        "echo ''",
        ""
    ]
    
    # Add empty file deletions
    if empty_files:
        script_lines.extend([
            "echo '🗑️  Removing empty files...'",
            ""
        ])
        
        for empty_file in empty_files:
            rel_path = os.path.relpath(empty_file, project_root)
            script_lines.append(f'echo "Removing empty file: {rel_path}"')
            script_lines.append(f'rm -f "{empty_file}"')
        
        script_lines.append("")
    
    # Add duplicate file analysis
    if duplicates:
        script_lines.extend([
            "echo '🔄 Analyzing duplicate files...'",
            "echo 'Please review these manually:'",
            ""
        ])
        
        for i, (hash_val, files) in enumerate(duplicates.items(), 1):
            script_lines.append(f"echo 'Duplicate group {i}:'")
            for file_path in files:
                rel_path = os.path.relpath(file_path, project_root)
                script_lines.append(f'echo "  - {rel_path}"')
            script_lines.append("echo ''")
    
    script_lines.extend([
        "echo '✅ Cleanup completed!'",
        "echo 'Review duplicate files manually and decide which ones to keep.'"
    ])
    
    # Write cleanup script
    cleanup_path = project_root / 'cleanup_duplicates.sh'
    with open(cleanup_path, 'w') as f:
        f.write('\n'.join(script_lines))
    
    os.chmod(cleanup_path, 0o755)
    
    return str(cleanup_path)

def main():
    start_time = time.time()
    
    try:
        results = analyze_project()
        
        elapsed = time.time() - start_time
        print(f"\n⏱️ Analysis completed in {elapsed:.2f} seconds")
        print(f"📝 Cleanup script generated: cleanup_duplicates.sh")
        print("\nTo clean up empty files automatically:")
        print("  bash cleanup_duplicates.sh")
        
        # Save detailed results
        with open('duplicate_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("📊 Detailed results saved to: duplicate_analysis_results.json")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
