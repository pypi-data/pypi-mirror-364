"""
Advanced LangGraph Tool Wrappers with Shell, Git, and Enhanced Code Analysis
Integrates the uploaded tools into LangGraph callable functions.
"""

import logging
import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain.tools import tool
from tools.file_operations import FileOperations
from tools.code_analysis import CodeAnalyzer
from tools.shell_operations import ShellOperations, GitOperations, WorkspaceManager
from tools.simple_code_search import FastCodeSearch
from tools.tool_usage_tracker import get_tool_tracker
from tools.security_scanner import scan_file_for_secrets, scan_directory_for_secrets, scan_recent_changes_for_secrets
# Direct MCP integration via langchain_mcp_adapters - no custom wrapper needed

logger = logging.getLogger(__name__)

class AdvancedLangGraphTools:
    """
    Advanced wrapper class that includes shell execution, git operations,
    and enhanced code analysis capabilities.
    """
    
    def __init__(self, repo_path: str, show_diffs: bool = True, debug_mode: bool = False, real_time_interface=None):
        self.repo_path = Path(repo_path)
        self.file_ops = FileOperations(repo_path, show_diffs=show_diffs, debug_mode=debug_mode)
        self.code_analyzer = CodeAnalyzer(repo_path)
        self.shell_ops = ShellOperations(repo_path)
        self.git_ops = GitOperations(repo_path)
        self.workspace_manager = WorkspaceManager(repo_path)
        self.code_search = FastCodeSearch(repo_path)
        self.show_diffs = show_diffs
        self.debug_mode = debug_mode
        self.real_time_interface = real_time_interface
        self._create_tools()
    
    def _create_tools(self):
        """Create advanced LangGraph tools."""
        file_ops = self.file_ops
        code_analyzer = self.code_analyzer
        shell_ops = self.shell_ops
        git_ops = self.git_ops
        workspace_manager = self.workspace_manager
        code_search = self.code_search
        repo_path = self.repo_path
        
        # Basic file operations (existing)
        @tool
        def create_file(filename: str, content: str) -> str:
            """
            Create a new file with the given content.
            
            Args:
                filename: Path to the file to create
                content: The complete content for the new file
                
            Example:
                create_file("hello.py", "print('Hello World')")
                
            Returns:
                Success message if file was created successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "create_file", {"filename": filename})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "create_file", False, error_msg)
                    return error_msg
                
                if content is None:
                    error_msg = "❌ Error: content parameter is required. Please provide the file content."
                    tracker.end_tool_call(call_id, "advanced_tools", "create_file", False, error_msg)
                    return error_msg
                
                result = file_ops.create_file(filename, content)
                success = result["success"]
                response = f"✅ Successfully created file: {filename}" if success else f"❌ Failed to create file: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "create_file", success, 
                                    result.get('error') if not success else None, 
                                    f"Created {filename}" if success else None)
                return response
            except Exception as e:
                error_msg = f"❌ Failed to create file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "create_file", False, str(e))
                return error_msg
        
        @tool
        def create_new_file(filename: str, content: str = "") -> str:
            """
            Create a new file with the specified filename and optional content.
            
            Args:
                filename: Name/path for the new file (can include directories)
                content: Optional content for the file (defaults to empty string)
                
            Example:
                create_new_file("my_script.py", "print('Hello World')")
                create_new_file("docs/readme.md", "# My Project")
                create_new_file("config.json", "{}")
                
            Returns:
                Success message if file was created successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "create_new_file", {"filename": filename, "content": content})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "create_new_file", False, error_msg)
                    return error_msg
                
                # Content can be empty string by default
                if content is None:
                    content = ""
                
                result = file_ops.create_file(filename, content)
                success = result["success"]
                response = f"✅ Successfully created new file: {filename}" if success else f"❌ Failed to create new file: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "create_new_file", success, 
                                    result.get('error') if not success else None, 
                                    f"Created new file {filename}" if success else None)
                return response
            except Exception as e:
                error_msg = f"❌ Failed to create new file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "create_new_file", False, str(e))
                return error_msg
        
        @tool
        def write_complete_file(filename: str, content: str) -> str:
            """
            Write complete content to a file (creates new or completely overwrites existing).
            
            Args:
                filename: Path to the file to write (creates new or overwrites existing)
                content: Complete content to write to the file
                
            Examples:
                write_complete_file("new_app.py", "import os\nprint('Hello World')")
                write_complete_file("empty_config.json", "{}")
                write_complete_file("blank_file.txt", "")
                
            Returns:
                Success message if file was written successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "write_complete_file", {"filename": filename, "content": content})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", False, error_msg)
                    return error_msg
                
                if content is None:
                    error_msg = "❌ Error: content parameter is required. Use empty string '' for blank files."
                    tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", False, error_msg)
                    return error_msg
                
                # Create or overwrite file with complete content
                result = file_ops.write_file(filename, content, append=False)
                success = result["success"]
                
                if success:
                    file_status = "created" if not Path(filename).exists() else "overwritten"
                    response = f"✅ Successfully wrote complete content to file: {filename} ({file_status})"
                else:
                    response = f"❌ Failed to write file: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", success, 
                                    result.get('error') if not success else None, 
                                    f"Wrote complete content to {filename}" if success else None)
                return response
            except Exception as e:
                error_msg = f"❌ Failed to write complete file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "write_complete_file", False, str(e))
                return error_msg
        
        @tool
        def replace_in_file(filename: str, old_text: str, new_text: str, max_replacements: int = -1) -> str:
            """
            Replace text in a file with debug and diff visualization.
            
            Args:
                filename: Path to the file to modify
                old_text: Text to find and replace
                new_text: Replacement text
                max_replacements: Maximum number of replacements (-1 for all occurrences)
                
            Examples:
                replace_in_file("config.py", "DEBUG = False", "DEBUG = True")
                replace_in_file("app.js", "localhost", "production.com", max_replacements=1)
                
            Returns:
                Success message with replacement count and diff visualization
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "replace_in_file", 
                                            {"filename": filename, "old_text": old_text, "new_text": new_text, "max_replacements": max_replacements})
            
            try:
                # Validate parameters
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, error_msg)
                    return error_msg
                
                if not old_text:
                    error_msg = "❌ Error: old_text parameter cannot be empty"
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, error_msg)
                    return error_msg
                
                result = file_ops.replace_in_file(filename, old_text, new_text, max_replacements)
                success = result["success"]
                
                if success:
                    replacements = result["replacements_made"]
                    response = f"✅ Successfully replaced {replacements} occurrence(s) in {filename}"
                    if result.get("diff_display"):
                        response += f"\n\n{result['diff_display']}"
                else:
                    response = f"❌ Failed to replace text: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", success, 
                                    result.get('error') if not success else None, 
                                    f"Replaced text in {filename}" if success else None)
                return response
            except Exception as e:
                error_msg = f"❌ Failed to replace text in {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, str(e))
                return error_msg
        
        @tool
        def search_in_file(filename: str, search_pattern: str, case_sensitive: bool = False) -> str:
            """
            Search for text patterns within a specific file and return matching lines with line numbers.
            
            Args:
                filename: Path to the file to search in
                search_pattern: Text pattern to search for (supports regex patterns)
                case_sensitive: Whether search should be case sensitive (default: False)
                
            Examples:
                search_in_file("app.py", "def main")
                search_in_file("config.json", '"port":', case_sensitive=True)
                search_in_file("README.md", "installation", case_sensitive=False)
                
            Returns:
                Matching lines with line numbers, or message if no matches found
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "search_in_file", {"filename": filename, "search_pattern": search_pattern, "case_sensitive": case_sensitive})
            
            try:
                import re
                from pathlib import Path
                
                # Validate parameters
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                
                if not search_pattern:
                    error_msg = "❌ Error: search_pattern parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                
                file_path = Path(filename)
                if not file_path.exists():
                    error_msg = f"❌ Error: File '{filename}' does not exist"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    # Prepare regex pattern
                    flags = 0 if case_sensitive else re.IGNORECASE
                    pattern = re.compile(search_pattern, flags)
                    
                    matches = []
                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            matches.append(f"Line {line_num}: {line.rstrip()}")
                    
                    if matches:
                        result = f"✅ Found {len(matches)} match(es) in '{filename}':\n" + "\n".join(matches)
                        success_msg = f"Found {len(matches)} matches for '{search_pattern}' in {filename}"
                    else:
                        result = f"❌ No matches found for pattern '{search_pattern}' in '{filename}'"
                        success_msg = f"No matches found for '{search_pattern}' in {filename}"
                    
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", True, None, success_msg)
                    return result
                    
                except UnicodeDecodeError:
                    error_msg = f"❌ Error: Cannot read file '{filename}' - appears to be binary or has encoding issues"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, error_msg)
                    return error_msg
                    
            except Exception as e:
                error_msg = f"❌ Failed to search in file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "search_in_file", False, str(e))
                return error_msg
        
        @tool
        def open_file(filename: str, line_number: int = 0, window_size: int = 50) -> str:
            """
            Open and read a file's content with smart defaults.
            
            Args:
                filename: Path to the file to open
                line_number: Starting line number (0 for beginning)
                window_size: Number of lines to read (50 default, -1 for entire file)
                
            Returns:
                File content with line numbers for easy reference
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "open_file", {"filename": filename, "line_number": line_number, "window_size": window_size})
            
            try:
                result = file_ops.open_file(filename, line_number, window_size)
                if result["success"]:
                    response = f"📄 File: {filename}\n{result['lines']}"
                    tracker.end_tool_call(call_id, "advanced_tools", "open_file", True, None, f"Opened {filename}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"❌ Failed to open file: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "open_file", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "open_file", False, str(e))
                raise
        
        @tool
        def edit_file(filename: str, new_content: str, line_number: int, num_lines: int = 1) -> str:
            """
            Edit a file by replacing content at specific lines.
            
            Args:
                filename: Path to the file to edit
                new_content: New content to insert
                line_number: Line number to start editing (1-based)
                num_lines: Number of lines to replace (default: 1)
                
            Example:
                edit_file("example.py", "print('Hello')", 1, 1)
                
            Returns:
                Success or error message
                
            Note: Consider using replace_in_file or rewrite_file for easier editing
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "edit_file", {"filename": filename, "line_number": line_number, "num_lines": num_lines})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "edit_file", False, error_msg)
                    return error_msg
                
                if new_content is None:
                    error_msg = "❌ Error: new_content parameter is required. Please provide the content to insert."
                    tracker.end_tool_call(call_id, "advanced_tools", "edit_file", False, error_msg)
                    return error_msg
                
                if not isinstance(line_number, int) or line_number < 1:
                    error_msg = "❌ Error: line_number must be a positive integer (1-based)"
                    tracker.end_tool_call(call_id, "advanced_tools", "edit_file", False, error_msg)
                    return error_msg
                
                # Read original content for diff display
                target_path = repo_path / filename
                original_content = ""
                if target_path.exists():
                    with open(target_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                
                result = file_ops.edit_file(filename, new_content, line_number, num_lines)
                if result["success"]:
                    # Show diff after successful edit
                    if self.show_diffs:
                        try:
                            with open(target_path, 'r', encoding='utf-8') as f:
                                final_content = f.read()
                            
                            from utils.diff_display import show_file_diff
                            from rich.console import Console
                            from rich.panel import Panel
                            
                            console = Console()
                            diff_output = show_file_diff(original_content, final_content, filename)
                            console.print(f"\n[bold yellow]📋 File Changes: {filename}[/bold yellow]")
                            console.print(Panel(
                                diff_output,
                                title=f"[bold]Edit: {filename}[/bold]",
                                border_style="blue",
                                expand=False
                            ))
                            console.print()
                        except:
                            pass
                    
                    response = f"✅ Successfully edited file: {filename}"
                    tracker.end_tool_call(call_id, "advanced_tools", "edit_file", True, None, f"Edited {filename}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"❌ Failed to edit file: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "edit_file", False, error_msg)
                    return response
            except Exception as e:
                error_msg = f"❌ Failed to edit file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "edit_file", False, str(e))
                return error_msg
        
        @tool
        def replace_in_file(filename: str, old_text: str, new_text: str, max_replacements: int = -1) -> str:
            """
            Replace text in a file using find and replace.
            
            Args:
                filename: Path to the file to edit
                old_text: Text to find and replace
                new_text: Text to replace with
                max_replacements: Maximum number of replacements (-1 for all)
                
            Example:
                replace_in_file("example.py", "old_function", "new_function")
                
            Returns:
                Success message with number of replacements made
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "replace_in_file", {"filename": filename, "old_text": old_text, "new_text": new_text})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, error_msg)
                    return error_msg
                
                if old_text is None:
                    error_msg = "❌ Error: old_text parameter is required. Please provide the text to find."
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, error_msg)
                    return error_msg
                
                if new_text is None:
                    error_msg = "❌ Error: new_text parameter is required. Please provide the replacement text."
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, error_msg)
                    return error_msg
                
                target_path = repo_path / filename
                if not target_path.exists():
                    response = f"❌ File not found: {filename}"
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, f"File not found: {filename}")
                    return response
                
                # Read file content
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Perform replacement
                if max_replacements == -1:
                    new_content = content.replace(old_text, new_text)
                    replacements = content.count(old_text)
                else:
                    new_content = content.replace(old_text, new_text, max_replacements)
                    replacements = min(content.count(old_text), max_replacements)
                
                if replacements == 0:
                    response = f"❌ Text '{old_text}' not found in {filename}"
                    tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, f"Text not found: {old_text}")
                    return response
                
                # Show diff before writing if enabled
                if self.show_diffs:
                    from utils.diff_display import show_file_diff
                    from rich.console import Console
                    from rich.panel import Panel
                    
                    console = Console()
                    diff_output = show_file_diff(content, new_content, filename)
                    console.print(f"\n[bold yellow]📋 File Changes: {filename}[/bold yellow]")
                    console.print(Panel(
                        diff_output,
                        title=f"[bold]Replace: {filename}[/bold]",
                        border_style="yellow",
                        expand=False
                    ))
                    console.print()
                
                # Write back to file
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                response = f"✅ Successfully replaced {replacements} occurrence(s) of '{old_text}' with '{new_text}' in {filename}"
                tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", True, None, f"Replaced {replacements} occurrences in {filename}")
                return response
            except Exception as e:
                error_msg = f"❌ Failed to replace text in {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "replace_in_file", False, str(e))
                return error_msg
        
        @tool
        def rewrite_file(filename: str, new_content: str) -> str:
            """
            Completely rewrite a file with new content.
            
            Args:
                filename: Path to the file to rewrite
                new_content: The complete new content for the file
                
            Example:
                rewrite_file("example.py", "print('Hello World')")
                
            Returns:
                Success message if file was rewritten successfully
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "rewrite_file", {"filename": filename})
            
            try:
                # Validate parameters explicitly
                if not filename:
                    error_msg = "❌ Error: filename parameter is required"
                    tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", False, error_msg)
                    return error_msg
                
                if new_content is None:
                    error_msg = "❌ Error: new_content parameter is required. Please provide the complete file content."
                    tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", False, error_msg)
                    return error_msg
                
                target_path = repo_path / filename
                
                # Read original content for diff display
                original_content = ""
                if target_path.exists():
                    with open(target_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    # Create backup
                    backup_path = target_path.with_suffix(target_path.suffix + '.backup')
                    backup_path.write_text(original_content)
                
                # Show diff before writing if enabled
                if self.show_diffs:
                    from utils.diff_display import show_file_diff
                    from rich.console import Console
                    from rich.panel import Panel
                    
                    console = Console()
                    diff_output = show_file_diff(original_content, new_content, filename)
                    console.print(f"\n[bold yellow]📋 File Changes: {filename}[/bold yellow]")
                    console.print(Panel(
                        diff_output,
                        title=f"[bold]Rewrite: {filename}[/bold]",
                        border_style="red",
                        expand=False
                    ))
                    console.print()
                
                # Write new content
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                response = f"✅ Successfully rewrote file: {filename}"
                tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", True, None, f"Rewrote {filename}")
                return response
            except Exception as e:
                error_msg = f"❌ Failed to rewrite file {filename}: {str(e)}"
                tracker.end_tool_call(call_id, "advanced_tools", "rewrite_file", False, str(e))
                return error_msg
        
        @tool
        def list_files(directory: str = ".") -> str:
            """
            List files and directories in the specified directory.
            
            Args:
                directory: Directory path to list (default: current directory)
                
            Returns:
                Formatted list of files and directories with clear separation
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "list_files", {"directory": directory})
            
            try:
                result = file_ops.list_files(directory)
                if result["success"]:
                    files = result["files"]
                    if files and isinstance(files[0], dict):
                        files_str = "\n".join([f.get('name', str(f)) for f in files[:20]])
                    else:
                        files_str = "\n".join(files[:20])
                    
                    dirs = result["directories"]
                    if dirs and isinstance(dirs[0], dict):
                        dirs_str = "\n".join([d.get('name', str(d)) for d in dirs[:10]])
                    else:
                        dirs_str = "\n".join(dirs[:10])
                    
                    response = f"📁 Files:\n{files_str}\n\n📂 Directories:\n{dirs_str}"
                    tracker.end_tool_call(call_id, "advanced_tools", "list_files", True, None, f"Listed {directory}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"❌ Failed to list files: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "list_files", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "list_files", False, str(e))
                raise
        
        # Shell execution capabilities
        @tool
        def execute_shell_command(command: str, timeout: int = 30) -> str:
            """
            Execute a shell command with timeout.
            
            Args:
                command: Shell command to execute
                timeout: Timeout in seconds (default: 30)
                
            Returns:
                Command output and status
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "execute_shell_command", {"command": command, "timeout": timeout})
            
            try:
                result = shell_ops.execute_command(command, timeout)
                success = result['success']
                response = f"✅ Command executed successfully:\n{result['stdout']}" if success else f"❌ Command failed (exit code {result['exit_code']}):\n{result['stderr']}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "execute_shell_command", success,
                                    result['stderr'] if not success else None,
                                    f"Executed: {command}" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "execute_shell_command", False, str(e))
                raise
        
        @tool
        def get_command_history() -> str:
            """
            Get the history of executed shell commands.
            
            Returns:
                Formatted list of recently executed commands with execution order
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "get_command_history", {})
            
            try:
                history = shell_ops.get_command_history()
                if not history:
                    response = "📜 No commands executed yet"
                else:
                    history_str = "\n".join([f"{i+1}. {cmd['command']}" for i, cmd in enumerate(history)])
                    response = f"📜 Recent command history:\n{history_str}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "get_command_history", True, None, f"Retrieved {len(history)} commands")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "get_command_history", False, str(e))
                raise
        
        # Git operations
        @tool
        def git_status() -> str:
            """
            Get git repository status showing changes, staged files, and branch info.
            
            Returns:
                Git status information including modified files and staging area
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "git_status", {})
            
            try:
                result = git_ops.git_status()
                if result['success']:
                    if result['stdout'].strip():
                        response = f"🔄 Git status:\n{result['stdout']}"
                    else:
                        response = "✅ Working directory clean"
                    tracker.end_tool_call(call_id, "advanced_tools", "git_status", True, None, "Retrieved git status")
                    return response
                else:
                    error_msg = result['stderr']
                    response = f"❌ Git status failed: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "git_status", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "git_status", False, str(e))
                raise
        
        @tool
        def git_diff(file_path: str = None) -> str:
            """
            Get git diff for changes.
            
            Args:
                file_path: Specific file to diff (optional)
                
            Returns:
                Git diff output
            """
            result = git_ops.git_diff(file_path)
            if result['success']:
                if result['stdout'].strip():
                    return f"📝 Git diff:\n{result['stdout']}"
                else:
                    return "✅ No changes to show"
            else:
                return f"❌ Git diff failed: {result['stderr']}"
        
        @tool
        def git_add(file_path: str) -> str:
            """
            Add file to git staging area.
            
            Args:
                file_path: Path to file to add
                
            Returns:
                Git add result
            """
            result = git_ops.git_add(file_path)
            if result['success']:
                return f"✅ Added {file_path} to git staging area"
            else:
                return f"❌ Git add failed: {result['stderr']}"
        
        @tool
        def git_commit(message: str) -> str:
            """
            Commit staged changes.
            
            Args:
                message: Commit message
                
            Returns:
                Git commit result
            """
            result = git_ops.git_commit(message)
            if result['success']:
                return f"✅ Committed changes: {message}"
            else:
                return f"❌ Git commit failed: {result['stderr']}"
        
        # Enhanced code analysis
        @tool
        def analyze_file_advanced(filename: str) -> str:
            """
            Advanced file analysis with detailed structure information.
            
            Args:
                filename: Path to the file to analyze
                
            Returns:
                Comprehensive analysis including language, structure, and components
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "analyze_file_advanced", {"filename": filename})
            
            try:
                result = code_analyzer.analyze_file(filename)
                if result["success"]:
                    response = f"""🔍 Advanced Analysis: {filename}

Language: {result['language']}
Lines: {result['line_count']}
Functions: {len(result['functions'])}
Classes: {len(result['classes'])}
Imports: {len(result['imports'])}

🔧 Functions:
{chr(10).join([f"  - {f['name']} (line {f['line_start']})" for f in result['functions'][:10]])}

📋 Classes:
{chr(10).join([f"  - {c['name']} (lines {c['line_start']}-{c['line_end']})" for c in result['classes'][:10]])}

📦 Imports:
{chr(10).join([f"  - {imp}" for imp in result['imports'][:10]])}"""
                    tracker.end_tool_call(call_id, "advanced_tools", "analyze_file_advanced", True, None, f"Analyzed {filename}")
                    return response
                else:
                    error_msg = result.get('error', 'Unknown error')
                    response = f"❌ Analysis failed: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "analyze_file_advanced", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "analyze_file_advanced", False, str(e))
                raise
        
        @tool
        def search_code_semantic(query: str, file_pattern: str = "*.py") -> str:
            """
            Semantic code search using pattern matching across files.
            
            Args:
                query: Search query (can be function names, class names, or code patterns)
                file_pattern: File pattern to search in (default: *.py for Python files)
                
            Returns:
                Search results with file paths and line numbers
                
            Examples:
                - search_code_semantic("def create_file") - finds function definitions
                - search_code_semantic("class Agent", "*.py") - finds class definitions
                - search_code_semantic("import langchain", "*") - finds imports
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "search_code_semantic", {"query": query, "file_pattern": file_pattern})
            
            try:
                # Use memory-mapped FastCodeSearch for optimized performance
                results = code_search.search(query, max_results=20)
                if results:
                    formatted_results = []
                    for result in results:
                        formatted_results.append(f"📄 {result.file_path}:{result.line_number} - {result.line_content[:80]}...")
                    response = f"🔍 Found {len(results)} matches for '{query}':\n" + "\n".join(formatted_results)
                    tracker.end_tool_call(call_id, "advanced_tools", "search_code_semantic", True, None, f"Found {len(results)} matches for '{query}'")
                else:
                    response = f"🔍 No matches found for '{query}'"
                    tracker.end_tool_call(call_id, "advanced_tools", "search_code_semantic", True, None, f"No matches for '{query}'")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "search_code_semantic", False, str(e))
                raise
        
        @tool
        def get_workspace_info() -> str:
            """
            Get comprehensive workspace information including files, directories, and project structure.
            
            Returns:
                Detailed workspace overview with file counts, types, and recent files
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "get_workspace_info", {})
            
            try:
                result = workspace_manager.get_workspace_info()
                if result['success']:
                    info = result['workspace_info']
                    branch_result = git_ops.git_branch()
                    branch = branch_result['stdout'].strip() if branch_result['success'] else 'Not a git repository'
                    
                    response = f"""🏢 Workspace Information:

📁 Repository: {info['repository_path']}
🌿 Git Branch: {branch}
📊 Total Files: {len(info['files'])}
📂 Directories: {len(info['directories'])}
💾 Size: {info['size_mb']:.2f} MB

🗂️ File Types:
{chr(10).join([f"  - {ext}: {count}" for ext, count in info['languages'].items()])}

📁 Recent Files:
{chr(10).join([f"  - {f['name']}" for f in info['files'][:10]])}"""
                    tracker.end_tool_call(call_id, "advanced_tools", "get_workspace_info", True, None, "Retrieved workspace info")
                    return response
                else:
                    error_msg = result['error']
                    response = f"❌ Workspace info error: {error_msg}"
                    tracker.end_tool_call(call_id, "advanced_tools", "get_workspace_info", False, error_msg)
                    return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "get_workspace_info", False, str(e))
                raise
        
        # Advanced code search tools
        @tool
        def find_function_definitions(function_name: str, language: str = "python") -> str:
            """
            Find function definitions across the codebase with file locations.
            
            Args:
                function_name: Name of the function to find (exact match or partial)
                language: Programming language (default: python, also supports: javascript, java, etc.)
                
            Returns:
                Function definition locations with file paths and line numbers
                
            Examples:
                - find_function_definitions("create_file") - finds create_file function
                - find_function_definitions("analyze", "python") - finds analyze functions
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "find_function_definitions", {"function_name": function_name, "language": language})
            
            try:
                # Use memory-mapped FastCodeSearch for optimized function search
                results = code_search.search_functions(function_name)
                if results:
                    formatted_results = []
                    for result in results:
                        formatted_results.append(f"🔧 {result.file_path}:{result.line_number} - {result.line_content[:80]}...")
                    response = f"🔍 Found {len(results)} function definitions for '{function_name}':\n" + "\n".join(formatted_results)
                    tracker.end_tool_call(call_id, "advanced_tools", "find_function_definitions", True, None, f"Found {len(results)} '{function_name}' functions")
                else:
                    response = f"🔍 No function definitions found for '{function_name}'"
                    tracker.end_tool_call(call_id, "advanced_tools", "find_function_definitions", True, None, f"No '{function_name}' functions found")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "find_function_definitions", False, str(e))
                raise
        
        @tool
        def find_class_definitions(class_name: str, language: str = "python") -> str:
            """
            Find class definitions across the codebase with inheritance info.
            
            Args:
                class_name: Name of the class to find (exact match or partial)
                language: Programming language (default: python, also supports: javascript, java, etc.)
                
            Returns:
                Class definition locations with file paths and line numbers
                
            Examples:
                - find_class_definitions("Agent") - finds Agent classes
                - find_class_definitions("Workflow", "python") - finds Workflow classes
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "find_class_definitions", {"class_name": class_name, "language": language})
            
            try:
                # Use memory-mapped FastCodeSearch for optimized class search  
                results = code_search.search(f"class {class_name}", max_results=20)
                if results:
                    formatted_results = []
                    for result in results:
                        formatted_results.append(f"🏗️ {result.file_path}:{result.line_number} - {result.line_content[:80]}...")
                    response = f"🔍 Found {len(results)} class definitions for '{class_name}':\n" + "\n".join(formatted_results)
                    tracker.end_tool_call(call_id, "advanced_tools", "find_class_definitions", True, None, f"Found {len(results)} '{class_name}' classes")
                else:
                    response = f"🔍 No class definitions found for '{class_name}'"
                    tracker.end_tool_call(call_id, "advanced_tools", "find_class_definitions", True, None, f"No '{class_name}' classes found")
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "find_class_definitions", False, str(e))
                raise
        
        @tool
        def find_imports(module_name: str, language: str = "python") -> str:
            """
            Find import statements across the codebase.
            
            Args:
                module_name: Name of the module to find imports for
                language: Programming language (default: python)
                
            Returns:
                Import statement locations
            """
            result = code_search.find_imports(module_name, language)
            if result['success']:
                if result['stdout'].strip():
                    return f"🔍 Found imports for '{module_name}':\n{result['stdout']}"
                else:
                    return f"🔍 No imports found for '{module_name}'"
            else:
                return f"❌ Search error: {result['stderr']}"
        
        @tool
        def get_directory_tree(max_depth: int = 3) -> str:
            """
            Get directory tree structure.
            
            Args:
                max_depth: Maximum depth to traverse (default: 3)
                
            Returns:
                Directory tree structure
            """
            result = workspace_manager.get_directory_tree(max_depth)
            if result['success']:
                return f"🌳 Directory tree:\n{result['stdout']}"
            else:
                return f"❌ Directory tree error: {result['stderr']}"
        
        @tool
        def search_files_by_name(pattern: str, file_type: str = "*") -> str:
            """
            Search for files by name pattern.
            
            Args:
                pattern: Pattern to search for in file names
                file_type: File type filter (default: all files)
                
            Returns:
                Matching file paths
            """
            result = workspace_manager.search_files(pattern, file_type)
            if result['success']:
                if result['stdout'].strip():
                    return f"🔍 Found files matching '{pattern}':\n{result['stdout']}"
                else:
                    return f"🔍 No files found matching '{pattern}'"
            else:
                return f"❌ File search error: {result['stderr']}"
        
        # Security scanning tools
        @tool
        def scan_file_security(filename: str) -> str:
            """
            Scan a specific file for potential secrets and security vulnerabilities.
            
            Args:
                filename: Path to the file to scan for secrets
                
            Returns:
                Security scan results showing potential secrets found
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scan_file_security", {"filename": filename})
            
            try:
                result = scan_file_for_secrets(filename)
                success = result["success"]
                
                if success:
                    secrets_count = result["secrets_found"]
                    if secrets_count > 0:
                        response = f"🔒 Security scan of {filename}: {secrets_count} potential secrets found!\n"
                        response += "⚠️  Please review and remove any sensitive information before committing."
                    else:
                        response = f"✅ Security scan of {filename}: No secrets detected"
                else:
                    response = f"❌ Security scan failed: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "scan_file_security", success, 
                                    result.get('error') if not success else None, 
                                    f"Scanned {filename} for secrets" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scan_file_security", False, str(e))
                raise
        
        @tool
        def scan_directory_security(directory_path: str = ".", max_files: int = 50) -> str:
            """
            Scan all files in a directory for potential secrets and security vulnerabilities.
            
            Args:
                directory_path: Path to the directory to scan (default: current directory)
                max_files: Maximum number of files to scan (default: 50)
                
            Returns:
                Comprehensive security scan results for all files in directory
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scan_directory_security", {"directory_path": directory_path})
            
            try:
                result = scan_directory_for_secrets(directory_path, max_files)
                success = result["success"]
                
                if success:
                    files_scanned = result["files_scanned"]
                    total_secrets = result["total_secrets"]
                    files_with_secrets = result["files_with_secrets"]
                    
                    response = f"🔒 Security scan of {directory_path}: {files_scanned} files scanned\n"
                    if total_secrets > 0:
                        response += f"⚠️  {total_secrets} potential secrets found in {files_with_secrets} files!\n"
                        response += "Please review and remove any sensitive information before committing."
                    else:
                        response += "✅ No secrets detected in any files"
                else:
                    response = f"❌ Security scan failed: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "scan_directory_security", success, 
                                    result.get('error') if not success else None, 
                                    f"Scanned {directory_path} for secrets" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scan_directory_security", False, str(e))
                raise
        
        @tool
        def scan_recent_changes_security() -> str:
            """
            Scan recently modified files for potential secrets and security vulnerabilities.
            
            Returns:
                Security scan results for recently modified files
            """
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call("advanced_tools", "scan_recent_changes_security", {})
            
            try:
                result = scan_recent_changes_for_secrets()
                success = result["success"]
                
                if success:
                    files_scanned = result["files_scanned"]
                    total_secrets = result["total_secrets"]
                    
                    response = f"🔒 Security scan of recent changes: {files_scanned} files scanned\n"
                    if total_secrets > 0:
                        response += f"⚠️  {total_secrets} potential secrets found in recent changes!\n"
                        response += "Please review and remove any sensitive information before committing."
                    else:
                        response += "✅ No secrets detected in recent changes"
                else:
                    response = f"❌ Security scan failed: {result.get('error', 'Unknown error')}"
                
                tracker.end_tool_call(call_id, "advanced_tools", "scan_recent_changes_security", success, 
                                    result.get('error') if not success else None, 
                                    "Scanned recent changes for secrets" if success else None)
                return response
            except Exception as e:
                tracker.end_tool_call(call_id, "advanced_tools", "scan_recent_changes_security", False, str(e))
                raise
        
# MCP tools are integrated directly via langchain_mcp_adapters - no management wrapper needed
        
        # Store tools as instance attributes
        self.create_file = create_file
        self.create_new_file = create_new_file
        self.write_complete_file = write_complete_file
        self.search_in_file = search_in_file
        self.open_file = open_file
        self.edit_file = edit_file
        self.replace_in_file = replace_in_file
        self.rewrite_file = rewrite_file
        self.list_files = list_files
        self.execute_shell_command = execute_shell_command
        self.get_command_history = get_command_history
        self.git_status = git_status
        self.git_diff = git_diff
        self.git_add = git_add
        self.git_commit = git_commit
        self.analyze_file_advanced = analyze_file_advanced
        self.search_code_semantic = search_code_semantic
        self.get_workspace_info = get_workspace_info
        self.find_function_definitions = find_function_definitions
        self.find_class_definitions = find_class_definitions
        self.find_imports = find_imports
        self.get_directory_tree = get_directory_tree
        self.search_files_by_name = search_files_by_name
        self.scan_file_security = scan_file_security
        self.scan_directory_security = scan_directory_security
        self.scan_recent_changes_security = scan_recent_changes_security
    
    def get_all_tools(self) -> List:
        """Get all available tools."""
        return [
            self.create_file,
            self.create_new_file,
            self.write_complete_file,
            self.search_in_file,
            self.open_file,
            self.edit_file,
            self.replace_in_file,
            self.rewrite_file,
            self.list_files,
            self.execute_shell_command,
            self.get_command_history,
            self.git_status,
            self.git_diff,
            self.git_add,
            self.git_commit,
            self.analyze_file_advanced,
            self.search_code_semantic,
            self.get_workspace_info,
            self.find_function_definitions,
            self.find_class_definitions,
            self.find_imports,
            self.get_directory_tree,
            self.search_files_by_name,
            self.scan_file_security,
            self.scan_directory_security,
            self.scan_recent_changes_security
        ]