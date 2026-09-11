"""hoon.ast — AST definitions.

Document is the root object; order is preserved (dict preserves insertion order on Python 3.7+).
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any

# Value is defined in value.py to avoid circular import; Document is simply dict[str, Value]
# Use string annotation for forward ref.

Document = Dict[str, Any]

def doc_from_pairs(pairs: List[Tuple[str, Any]]) -> Document:
    """Create ordered Document from pairs, preserving order."""
    return {k: v for k, v in pairs}
