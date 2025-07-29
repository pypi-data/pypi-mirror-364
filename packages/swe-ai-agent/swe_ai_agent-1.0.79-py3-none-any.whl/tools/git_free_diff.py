#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 SWE Agent Contributors

"""
Git-free diff implementation using Python's difflib module.
Provides file comparison and diff display without requiring git.
"""

import difflib
import os
import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class GitFreeDiff:
    """
    File diff implementation that doesn't require git.
    Tracks file changes using checksums and timestamps.
    """
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir)
        self.state_file = self.workspace_dir / ".swe_agent_state.json"
        self.file_states = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load previously saved file states."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_state(self):
        """Save current file states."""
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
    
    def _get_file_lines(self, file_path: Path) -> List[str]:
        """Get file content as lines."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except:
            return []
    
    def snapshot_workspace(self) -> int:
        """Take a snapshot of current workspace state."""
        snapshot_id = int(time.time())
        
        for file_path in self.workspace_dir.rglob("*"):
            if file_path.is_file() and not self._should_ignore(file_path):
                rel_path = str(file_path.relative_to(self.workspace_dir))
                file_hash = self._get_file_hash(file_path)
                
                if rel_path not in self.file_states:
                    self.file_states[rel_path] = {}
                
                self.file_states[rel_path][snapshot_id] = {
                    'hash': file_hash,
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime,
                    'lines': len(self._get_file_lines(file_path))
                }
        
        self._save_state()
        return snapshot_id
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = [
            '.git', '__pycache__', '.pyc', '.pyo', '.pyd',
            'node_modules', '.env', '.venv', 'venv',
            '.swe_agent_state.json', '.DS_Store'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    def get_changes_since_snapshot(self, snapshot_id: int) -> List[Tuple[str, str]]:
        """Get list of changed files since snapshot."""
        changes = []
        
        for file_path in self.workspace_dir.rglob("*"):
            if file_path.is_file() and not self._should_ignore(file_path):
                rel_path = str(file_path.relative_to(self.workspace_dir))
                current_hash = self._get_file_hash(file_path)
                
                if rel_path in self.file_states and snapshot_id in self.file_states[rel_path]:
                    old_hash = self.file_states[rel_path][snapshot_id]['hash']
                    if current_hash != old_hash:
                        changes.append((rel_path, 'modified'))
                else:
                    changes.append((rel_path, 'added'))
        
        # Check for deleted files
        for rel_path in self.file_states:
            if snapshot_id in self.file_states[rel_path]:
                full_path = self.workspace_dir / rel_path
                if not full_path.exists():
                    changes.append((rel_path, 'deleted'))
        
        return changes
    
    def get_file_diff(self, file_path: str, snapshot_id: Optional[int] = None) -> str:
        """Get diff for a specific file."""
        full_path = self.workspace_dir / file_path
        
        if not full_path.exists():
            return f"File {file_path} does not exist"
        
        current_lines = self._get_file_lines(full_path)
        
        if snapshot_id and file_path in self.file_states and snapshot_id in self.file_states[file_path]:
            # Compare with snapshot
            old_lines = self._get_stored_lines(file_path, snapshot_id)
        else:
            # Compare with empty file (show as new)
            old_lines = []
        
        diff = difflib.unified_diff(
            old_lines,
            current_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        
        return "\n".join(diff)
    
    def _get_stored_lines(self, file_path: str, snapshot_id: int) -> List[str]:
        """Get stored file lines from snapshot (simplified - would need to store actual content)."""
        # In a real implementation, you'd store the actual file content
        # For now, return empty list as fallback
        return []
    
    def get_colored_diff(self, file_path: str, snapshot_id: Optional[int] = None) -> List[str]:
        """Get diff with color codes for Rich console."""
        diff_text = self.get_file_diff(file_path, snapshot_id)
        colored_lines = []
        
        for line in diff_text.split('\n'):
            if line.startswith('+++'):
                colored_lines.append(f"[blue]{line}[/blue]")
            elif line.startswith('---'):
                colored_lines.append(f"[blue]{line}[/blue]")
            elif line.startswith('@@'):
                colored_lines.append(f"[blue]{line}[/blue]")
            elif line.startswith('+'):
                colored_lines.append(f"[green]{line}[/green]")
            elif line.startswith('-'):
                colored_lines.append(f"[red]{line}[/red]")
            else:
                colored_lines.append(line)
        
        return colored_lines
    
    def get_simple_changes(self) -> List[Tuple[str, str, str]]:
        """Get simple list of recent changes without full diff."""
        changes = []
        
        for file_path in self.workspace_dir.rglob("*"):
            if file_path.is_file() and not self._should_ignore(file_path):
                rel_path = str(file_path.relative_to(self.workspace_dir))
                
                # Check if file is recently modified (within last 10 minutes)
                current_time = time.time()
                file_modified = file_path.stat().st_mtime
                
                if current_time - file_modified < 600:  # 10 minutes
                    file_size = file_path.stat().st_size
                    changes.append((rel_path, 'modified', f"{file_size} bytes"))
        
        return changes

# Usage examples
if __name__ == "__main__":
    # Example usage
    differ = GitFreeDiff()
    
    # Take a snapshot
    snapshot_id = differ.snapshot_workspace()
    print(f"Snapshot taken: {snapshot_id}")
    
    # Later, check for changes
    changes = differ.get_changes_since_snapshot(snapshot_id)
    print(f"Changes detected: {changes}")
    
    # Get diff for a specific file
    if changes:
        file_path = changes[0][0]
        diff = differ.get_file_diff(file_path, snapshot_id)
        print(f"Diff for {file_path}:")
        print(diff)