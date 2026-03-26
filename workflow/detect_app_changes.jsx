#!/usr/bin/env python3
"""
Detect changes in apps folder using git diff
Returns list of changed/added YAML files
"""

import subprocess
import os
import json
from pathlib import Path
from typing import List, Dict

class AppChangeDetector:
    def __init__(self, apps_dir: str = "apps"):
        self.apps_dir = Path(apps_dir)
        self.project_root = Path(__file__).parent.parent
        
    def get_changed_files(self) -> List[Dict[str, str]]:
        """
        Detect changed YAML files in apps directory using git diff
        Returns list of dicts with file path and change type
        """
        os.chdir(self.project_root)
        
        try:
            # Get uncommitted changes
            result = subprocess.run(
                ['git', 'diff', '--name-status', 'HEAD', str(self.apps_dir)],
                capture_output=True,
                text=True,
                check=True
            )
            
            uncommitted = self._parse_git_output(result.stdout)
            
            # Get staged changes
            result = subprocess.run(
                ['git', 'diff', '--name-status', '--cached', str(self.apps_dir)],
                capture_output=True,
                text=True,
                check=True
            )
            
            staged = self._parse_git_output(result.stdout)
            
            # Combine and deduplicate
            all_changes = {change['path']: change for change in uncommitted + staged}
            
            return list(all_changes.values())
            
        except subprocess.CalledProcessError as e:
            print(f"Error running git command: {e}")
            return []
    
    def _parse_git_output(self, output: str) -> List[Dict[str, str]]:
        """Parse git diff output into structured format"""
        changes = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
                
            parts = line.split('\t')
            if len(parts) < 2:
                continue
                
            status = parts[0]
            filepath = parts[1]
            
            # Only process YAML files
            if not filepath.endswith(('.yaml', '.yml')):
                continue
            
            change_type = self._map_status(status)
            
            changes.append({
                'path': filepath,
                'type': change_type,
                'status': status,
                'app_name': Path(filepath).stem
            })
        
        return changes
    
    def _map_status(self, status: str) -> str:
        """Map git status codes to readable types"""
        mapping = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied'
        }
        return mapping.get(status[0], 'unknown')
    
    def get_file_content(self, filepath: str) -> str:
        """Read content of a changed file"""
        full_path = self.project_root / filepath
        
        if not full_path.exists():
            return ""
        
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def get_diff_content(self, filepath: str) -> str:
        """Get the actual diff for a file"""
        os.chdir(self.project_root)
        
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD', filepath],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting diff for {filepath}: {e}")
            return ""


def main():
    """Main function for testing"""
    detector = AppChangeDetector()
    changes = detector.get_changed_files()
    
    if not changes:
        print("No changes detected in apps folder")
        return
    
    print(f"Found {len(changes)} changed file(s):")
    print(json.dumps(changes, indent=2))
    
    # Show content of changed files
    for change in changes:
        print(f"\n{'='*60}")
        print(f"File: {change['path']} ({change['type']})")
        print(f"{'='*60}")
        
        if change['type'] != 'deleted':
            content = detector.get_file_content(change['path'])
            print(content[:500] + "..." if len(content) > 500 else content)


if __name__ == "__main__":
    main()
