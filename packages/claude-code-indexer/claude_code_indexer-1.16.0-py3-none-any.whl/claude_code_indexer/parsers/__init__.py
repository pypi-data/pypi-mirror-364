#!/usr/bin/env python3
"""
Parser system for Multi-Language Code Indexing
"""

from .base_parser import BaseParser, CompositeParser, CodeNode, CodeRelationship, ParseResult
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser
from .java_parser import JavaParser
from .autoit_parser import AutoItParser

__all__ = [
    'BaseParser',
    'CompositeParser', 
    'CodeNode',
    'CodeRelationship',
    'ParseResult',
    'PythonParser',
    'JavaScriptParser',
    'JavaParser',
    'AutoItParser',
    'create_default_parser',
    'get_supported_extensions'
]

def create_default_parser() -> CompositeParser:
    """Create a composite parser with all available language parsers"""
    composite = CompositeParser()
    
    # Add all language parsers
    composite.add_parser(PythonParser())
    composite.add_parser(JavaScriptParser())
    composite.add_parser(JavaParser())
    composite.add_parser(AutoItParser())
    
    return composite

def get_supported_extensions():
    """Get all supported file extensions"""
    parser = create_default_parser()
    extensions = set()
    for p in parser.parsers:
        extensions.update(p.supported_extensions)
    return extensions