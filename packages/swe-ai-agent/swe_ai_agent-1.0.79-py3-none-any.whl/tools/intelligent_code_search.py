# SPDX-License-Identifier: Apache-2.0

"""
Simple Text-Based Code Search System
Fast text matching across all files in workspace directory - no Whoosh, no indexing.
"""

from .simple_code_search import (
    FastCodeSearch,
    SearchResult,
    search_code_patterns,
    find_function_definitions,
    find_class_definitions, 
    find_import_statements,
    get_function_definition_and_usages,
    analyze_code_structure,
    CODE_EXTENSIONS,
    SKIP_DIRS,
    LanguageDetector
)

# Legacy compatibility class
class IntelligentCodeSearch:
    """Legacy compatibility wrapper for the new simple search system."""
    
    def __init__(self, workspace_dir: str = None, auto_index: bool = True):
        """Initialize with simple text search (ignoring auto_index parameter)."""
        self.searcher = FastCodeSearch(workspace_dir)
        self.indexed = True  # Always "indexed" since no indexing needed
    
    def search_patterns(self, pattern: str, max_results: int = 100) -> list:
        """Search for patterns using simple text matching."""
        return search_code_patterns(pattern, str(self.searcher.workspace_dir), max_results=max_results)
    
    def get_function_definition_and_usages(self, function_name: str) -> dict:
        """Get function definitions and usages."""
        return get_function_definition_and_usages(function_name, str(self.searcher.workspace_dir))
    
    def analyze_code_structure(self, file_path: str) -> dict:
        """Analyze code structure."""
        return analyze_code_structure(file_path)
    
    def find_function_definitions(self, function_name: str) -> list:
        """Find function definitions."""
        return find_function_definitions(function_name, str(self.searcher.workspace_dir))
    
    def find_class_definitions(self, class_name: str) -> list:
        """Find class definitions."""  
        return find_class_definitions(class_name, str(self.searcher.workspace_dir))
    
    def find_import_statements(self, import_name: str) -> list:
        """Find import statements."""
        return find_import_statements(import_name, str(self.searcher.workspace_dir))

# Export all the main functions and classes
__all__ = [
    'IntelligentCodeSearch',
    'FastCodeSearch', 
    'SearchResult',
    'search_code_patterns',
    'find_function_definitions',
    'find_class_definitions',
    'find_import_statements',
    'get_function_definition_and_usages',
    'analyze_code_structure',
    'LanguageDetector'
]