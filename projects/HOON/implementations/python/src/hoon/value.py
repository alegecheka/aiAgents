"""hoon.value — Value type alias and helpers.

HOON values:
  null, bool, int, float, str, list[Value], Document
"""
from __future__ import annotations
import re
from typing import Union, List, Dict, Any

# Forward: Document is Dict[str, Value]
Value = Union[None, bool, int, float, str, List[Any], Dict[str, Any]]

_BARE_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*$')

def is_bare_key(k: str) -> bool:
    return bool(_BARE_KEY_RE.match(k))
