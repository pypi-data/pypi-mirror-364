#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 SWE Agent Contributors

"""
Backup and diff system for tracking actual file changes.
Creates backups before modifications and provides real diffs.
"""

import os
import shutil
import time
import hashlib
import json
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class BackupDiffSystem:
    """
    System for creating backups and generating actual diffs.
    """
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir)
        self.backup_dir = self.workspace_dir / ".swe_backups"
        self.state_file = self.workspace_dir / ".swe_file_states.json"
        self.backup_dir.mkdir(exist_ok=True)
        self.file_states = self._load_states()
    
    def _load_states(self) -> Dict[str, Any]:
        """Load file states from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_states(self):
        """Save file states to disk."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.file_states, f, indent=2)
        except:
            pass
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def backup_file(self, file_path: str) -> bool:
        """
        Create a backup of a file before modification.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            True if backup was created successfully
        """
        try:
            full_path = self.workspace_dir / file_path
            if not full_path.exists():
                return False
            
            # Create backup filename with timestamp
            timestamp = int(time.time())
            backup_name = f"{file_path.replace('/', '_')}_{timestamp}.backup"
            backup_path = self.backup_dir / backup_name
            
            # Create backup directory structure if needed
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file to backup
            shutil.copy2(full_path, backup_path)
            
            # Update file states
            file_hash = self._get_file_hash(full_path)
            self.file_states[file_path] = {
                'last_backup': str(backup_path),
                'last_hash': file_hash,
                'timestamp': timestamp
            }
            
            self._save_states()
            return True
            
        except Exception:
            return False
    
    def get_file_diff(self, file_path: str) -> List[str]:
        """
        Get diff between current file and its last backup.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of colored diff lines for Rich console
        """
        try:
            full_path = self.workspace_dir / file_path
            
            if not full_path.exists():
                return [f"[red]File {file_path} does not exist[/red]"]
            
            # Get current content
            with open(full_path, 'r', encoding='utf-8') as f:
                current_lines = f.readlines()
            
            # Get backup content if it exists
            if file_path in self.file_states:
                backup_path = Path(self.file_states[file_path]['last_backup'])
                if backup_path.exists():
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_lines = f.readlines()
                else:
                    backup_lines = []
            else:
                backup_lines = []
            
            # Generate diff
            diff = difflib.unified_diff(
                backup_lines,
                current_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm=""
            )
            
            # Color the diff for Rich console
            colored_lines = []
            for line in diff:
                if line.startswith('+++'):
                    colored_lines.append(f"[blue]{line}[/blue]")
                elif line.startswith('---'):
                    colored_lines.append(f"[blue]{line}[/blue]")
                elif line.startswith('@@'):
                    colored_lines.append(f"[cyan]{line}[/cyan]")
                elif line.startswith('+'):
                    colored_lines.append(f"[green]{line}[/green]")
                elif line.startswith('-'):
                    colored_lines.append(f"[red]{line}[/red]")
                else:
                    colored_lines.append(f"[dim]{line}[/dim]")
            
            return colored_lines
            
        except Exception as e:
            return [f"[red]Error generating diff: {str(e)}[/red]"]
    
    def get_recent_changes(self, minutes: int = 10) -> List[Tuple[str, str, str]]:
        """
        Get files that have been modified recently.
        
        Args:
            minutes: Files modified within this many minutes
            
        Returns:
            List of (filepath, status, diff_preview) tuples
        """
        changes = []
        current_time = time.time()
        cutoff_time = current_time - (minutes * 60)
        
        try:
            for file_path in self.file_states:
                file_info = self.file_states[file_path]
                
                if file_info['timestamp'] > cutoff_time:
                    full_path = self.workspace_dir / file_path
                    
                    if full_path.exists():
                        # Check if file has actually changed
                        current_hash = self._get_file_hash(full_path)
                        if current_hash != file_info['last_hash']:
                            # Generate diff preview
                            diff_lines = self.get_file_diff(file_path)
                            if diff_lines:
                                # Take first few lines of diff as preview
                                preview = '\n'.join(diff_lines[:5])
                                changes.append((file_path, 'modified', preview))
                                
                                # Update hash
                                file_info['last_hash'] = current_hash
                                self._save_states()
        except Exception:
            pass
        
        return changes
    
    def cleanup_old_backups(self, days: int = 7):
        """
        Clean up backups older than specified days.
        
        Args:
            days: Remove backups older than this many days
        """
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            for backup_file in self.backup_dir.glob("*.backup"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    
        except Exception:
            pass

# Global instance
backup_diff_system = BackupDiffSystem()

def create_backup(file_path: str) -> bool:
    """Create a backup of a file."""
    return backup_diff_system.backup_file(file_path)

def get_file_diff(file_path: str) -> List[str]:
    """Get diff for a file."""
    return backup_diff_system.get_file_diff(file_path)

def get_recent_changes_with_diff(minutes: int = 10) -> List[Tuple[str, str, str]]:
    """Get recent changes with actual diff content."""
    return backup_diff_system.get_recent_changes(minutes)

# Example usage
if __name__ == "__main__":
    # Test the backup system
    system = BackupDiffSystem()
    
    # Create a test file
    test_file = "test_file.txt"
    with open(test_file, 'w') as f:
        f.write("Original content\n")
    
    # Create backup
    system.backup_file(test_file)
    
    # Modify file
    with open(test_file, 'w') as f:
        f.write("Modified content\nWith new lines\n")
    
    # Get diff
    diff = system.get_file_diff(test_file)
    print("Diff:")
    for line in diff:
        print(line)
    
    # Clean up
    os.remove(test_file)