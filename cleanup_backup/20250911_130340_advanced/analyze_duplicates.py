#!/usr/bin/env python3
"""
Comprehensive Duplicate and Empty File Analysis
Analyzes the entire VIP_RIDE_PLATFORM codebase for:
1. Empty files
2. Duplicate files (by content)
3. Similar files with different names
4. Obsolete files that can be safely removed
"""

import os
import hashlib
from pathlib import Path
import difflib
from typing import Dict, List, Set, Tuple
import json


class DuplicateAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.empty_files: List[Path] = []
        self.duplicates: Dict[str, List[Path]] = {}  # hash -> list of files
        self.similar_files: List[Tuple[Path, Path, float]] = []
        self.excluded_dirs = {
            '.git', '__pycache__', 'node_modules', '.dart_tool', 'build',
            'dist', '.idea', '.vscode', 'migrations', '.flutter-plugins-dependencies',
            'backup_old_files', 'logs'
        }
        self.excluded_extensions = {
            '.pyc', '.pyo', '.log', '.tmp', '.cache', '.lock'
        }

    def get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of file content"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except (IOError, OSError):
            return None

    def get_file_content_normalized(self, filepath: Path) -> str:
        """Get normalized file content for comparison"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Normalize whitespace and remove comments for better comparison
                lines = [line.strip() for line in content.split('\n') 
                        if line.strip() and not line.strip().startswith('#')]
                return '\n'.join(lines)
        except (IOError, OSError, UnicodeDecodeError):
            return ""

    def should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped"""
        # Skip excluded directories
        for part in path.parts:
            if part in self.excluded_dirs:
                return True
        
        # Skip excluded extensions
        if path.suffix in self.excluded_extensions:
            return True
            
        # Skip binary files
        if path.suffix in {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip'}:
            return True
            
        return False

    def analyze_files(self):
        """Analyze all files in the project"""
        print(f"Analyzing files in: {self.root_path}")
        
        file_hashes: Dict[str, List[Path]] = {}
        file_contents: Dict[Path, str] = {}
        
        # Walk through all files
        for filepath in self.root_path.rglob('*'):
            if filepath.is_file() and not self.should_skip_path(filepath):
                try:
                    # Check if file is empty
                    if filepath.stat().st_size == 0:
                        self.empty_files.append(filepath)
                        continue
                    
                    # Get file hash for exact duplicates
                    file_hash = self.get_file_hash(filepath)
                    if file_hash:
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(filepath)
                    
                    # Get content for similarity analysis
                    if filepath.suffix in {'.py', '.dart', '.js', '.ts', '.md', '.txt', '.yml', '.yaml'}:
                        content = self.get_file_content_normalized(filepath)
                        if content:
                            file_contents[filepath] = content
                            
                except (OSError, IOError) as e:
                    print(f"Error processing {filepath}: {e}")
        
        # Find exact duplicates
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.duplicates[file_hash] = files
        
        # Find similar files
        self.find_similar_files(file_contents)

    def find_similar_files(self, file_contents: Dict[Path, str]):
        """Find files with similar content"""
        print("Analyzing file similarity...")
        
        files = list(file_contents.keys())
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                # Skip if files are already exact duplicates
                hash1 = self.get_file_hash(file1)
                hash2 = self.get_file_hash(file2)
                if hash1 == hash2:
                    continue
                    
                # Calculate similarity
                content1 = file_contents[file1]
                content2 = file_contents[file2]
                
                similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
                
                # Consider files similar if they have >85% similarity
                if similarity > 0.85:
                    self.similar_files.append((file1, file2, similarity))

    def identify_suspicious_patterns(self) -> Dict[str, List[Path]]:
        """Identify files with suspicious naming patterns"""
        suspicious = {}
        
        all_files = list(self.root_path.rglob('*'))
        
        patterns = {
            'backup_files': ['_backup', '_old', '_bak', '.bak'],
            'temporary_files': ['_temp', '_tmp', '.tmp'],
            'new_files': ['_new', '.new'],
            'test_files_in_root': [],  # Will be filled below
            'consolidation_files': ['consolidate_', 'merge_', 'combine_']
        }
        
        # Find test files in root directory
        for filepath in all_files:
            if (filepath.is_file() and 
                filepath.parent == self.root_path and 
                (filepath.stem.startswith('test_') or 'test' in filepath.stem.lower())):
                if 'test_files_in_root' not in suspicious:
                    suspicious['test_files_in_root'] = []
                suspicious['test_files_in_root'].append(filepath)
        
        # Check for other patterns
        for pattern_name, pattern_list in patterns.items():
            if pattern_name == 'test_files_in_root':
                continue
                
            matching_files = []
            for filepath in all_files:
                if filepath.is_file():
                    filename = filepath.name.lower()
                    for pattern in pattern_list:
                        if pattern in filename:
                            matching_files.append(filepath)
                            break
            
            if matching_files:
                suspicious[pattern_name] = matching_files
        
        return suspicious

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        report = ["=" * 80]
        report.append("VIP RIDE PLATFORM - DUPLICATE & EMPTY FILE ANALYSIS")
        report.append("=" * 80)
        report.append()
        
        # Empty files
        report.append(f"📄 EMPTY FILES ({len(self.empty_files)} found):")
        report.append("-" * 40)
        if self.empty_files:
            for filepath in sorted(self.empty_files):
                rel_path = filepath.relative_to(self.root_path)
                report.append(f"❌ {rel_path}")
        else:
            report.append("✅ No empty files found")
        report.append()
        
        # Exact duplicates
        report.append(f"🔗 EXACT DUPLICATES ({len(self.duplicates)} groups found):")
        report.append("-" * 40)
        if self.duplicates:
            for i, (file_hash, files) in enumerate(self.duplicates.items(), 1):
                report.append(f"Group {i} (hash: {file_hash[:8]}...):")
                for filepath in sorted(files):
                    rel_path = filepath.relative_to(self.root_path)
                    size = filepath.stat().st_size
                    report.append(f"  📂 {rel_path} ({size} bytes)")
                report.append()
        else:
            report.append("✅ No exact duplicates found")
        report.append()
        
        # Similar files
        report.append(f"🔍 SIMILAR FILES ({len(self.similar_files)} pairs found):")
        report.append("-" * 40)
        if self.similar_files:
            for file1, file2, similarity in sorted(self.similar_files, 
                                                  key=lambda x: x[2], reverse=True):
                rel_path1 = file1.relative_to(self.root_path)
                rel_path2 = file2.relative_to(self.root_path)
                report.append(f"📊 Similarity: {similarity:.1%}")
                report.append(f"  📂 {rel_path1}")
                report.append(f"  📂 {rel_path2}")
                report.append()
        else:
            report.append("✅ No similar files found")
        report.append()
        
        # Suspicious patterns
        suspicious = self.identify_suspicious_patterns()
        report.append(f"⚠️  SUSPICIOUS PATTERNS ({len(suspicious)} types found):")
        report.append("-" * 40)
        if suspicious:
            for pattern_name, files in suspicious.items():
                report.append(f"{pattern_name.replace('_', ' ').title()}:")
                for filepath in sorted(files)[:10]:  # Limit to first 10
                    rel_path = filepath.relative_to(self.root_path)
                    report.append(f"  ⚠️  {rel_path}")
                if len(files) > 10:
                    report.append(f"  ... and {len(files) - 10} more")
                report.append()
        else:
            report.append("✅ No suspicious patterns found")
        
        return '\n'.join(report)

    def generate_cleanup_recommendations(self) -> List[str]:
        """Generate specific cleanup recommendations"""
        recommendations = []
        
        # Empty files
        if self.empty_files:
            recommendations.append("🗑️ REMOVE EMPTY FILES:")
            for filepath in sorted(self.empty_files):
                rel_path = filepath.relative_to(self.root_path)
                recommendations.append(f"rm '{rel_path}'")
            recommendations.append("")
        
        # Exact duplicates
        if self.duplicates:
            recommendations.append("🔗 HANDLE EXACT DUPLICATES:")
            for files in self.duplicates.values():
                if len(files) > 1:
                    # Keep the first file, suggest removing others
                    files_sorted = sorted(files)
                    keep_file = files_sorted[0]
                    remove_files = files_sorted[1:]
                    
                    rel_keep = keep_file.relative_to(self.root_path)
                    recommendations.append(f"# Keep: {rel_keep}")
                    for remove_file in remove_files:
                        rel_remove = remove_file.relative_to(self.root_path)
                        recommendations.append(f"rm '{rel_remove}'")
                    recommendations.append("")
        
        # Similar files that might be duplicates
        if self.similar_files:
            recommendations.append("🔍 REVIEW SIMILAR FILES (Manual Review Required):")
            for file1, file2, similarity in self.similar_files:
                if similarity > 0.95:  # Very high similarity
                    rel_path1 = file1.relative_to(self.root_path)
                    rel_path2 = file2.relative_to(self.root_path)
                    recommendations.append(f"# {similarity:.1%} similarity - likely duplicates:")
                    recommendations.append(f"# Compare: {rel_path1}")
                    recommendations.append(f"# Against: {rel_path2}")
                    recommendations.append("")
        
        return recommendations


def main():
    """Main analysis function"""
    project_root = "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform"
    
    print("Starting comprehensive duplicate and empty file analysis...")
    analyzer = DuplicateAnalyzer(project_root)
    analyzer.analyze_files()
    
    # Generate report
    report = analyzer.generate_report()
    print(report)
    
    # Save report
    report_path = Path(project_root) / "DUPLICATE_ANALYSIS_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Generate cleanup recommendations
    recommendations = analyzer.generate_cleanup_recommendations()
    if recommendations:
        cleanup_path = Path(project_root) / "cleanup_commands.sh"
        with open(cleanup_path, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n")
            f.write("# Cleanup commands generated by duplicate analyzer\n")
            f.write("# Review carefully before executing!\n\n")
            f.write('\n'.join(recommendations))
        
        print(f"\n📝 Cleanup recommendations saved to: {cleanup_path}")
        print(f"📊 Full report saved to: {report_path}")


if __name__ == "__main__":
    main()
