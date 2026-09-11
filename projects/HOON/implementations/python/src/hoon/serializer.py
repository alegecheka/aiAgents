"""
hoon.serializer — HOON <-> JSON conversion (strict mapping).

Strict mapping (lossless except for HOON specifics that JSON cannot represent):

  HOON string / text  -> JSON string   (escapes decoded, triple-quoted is just string)
  HOON integer (decimal or 0x) -> JSON number (int, hex loses 0x form -> decimal)
  HOON float           -> JSON number
  HOON bool / null     -> JSON bool / null
  HOON array           -> JSON array
  HOON object (including root) -> JSON object (key order preserved, comments dropped)

Reverse:

  JSON string  -> HOON string (double-quoted, multiline -> triple-quoted)
  JSON number (int) -> HOON integer (decimal)
  JSON number (float) -> HOON float
  JSON bool/null -> HOON bool/null
  JSON array -> HOON array
  JSON object -> HOON object (`{{{ ... }}}` for root, `{ ... }` nested)
  JSON object keys that need quoting are quoted.
"""
from __future__ import annotations
import json
from typing import Any

from .parser import parse, ParseError
from .value import is_bare_key

def _escape_hoon_string(s: str) -> str:
    out = ['"']
    for c in s:
        if c == '"':
            out.append('\\"')
        elif c == '\\':
            out.append('\\\\')
        elif c == '\n':
            out.append('\\n')
        elif c == '\t':
            out.append('\\t')
        elif c == '\r':
            out.append('\\r')
        else:
            code = ord(c)
            if code < 0x20:
                out.append(f"\\u{code:04X}")
            else:
                out.append(c)
    out.append('"')
    return "".join(out)

def _encode_hoon_value(v: Any, indent: int = 0) -> str:
    """Encode Python value (from json.loads or hoon parse) as HOON value syntax."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int) and not isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        s = f"{v:.15g}" if abs(v) not in (float('inf'),) else str(v)
        if '.' not in s and 'e' not in s and 'E' not in s:
            pass
        return s
    if isinstance(v, str):
        if "\n" in v:
            escaped = v.replace('"""', '\\"""')
            return f'"""\n{escaped}\n"""'
        else:
            return _escape_hoon_string(v)
    if isinstance(v, list):
        if not v:
            return "[]"
        inner = ", ".join(_encode_hoon_value(x, indent) for x in v)
        return f"[{inner}]"
    if isinstance(v, dict):
        if not v:
            return "{}"
        parts = []
        for k, val in v.items():
            key_repr = k if is_bare_key(k) else _escape_hoon_string(k)
            val_repr = _encode_hoon_value(val, indent + 1)
            parts.append(f"{key_repr}: {val_repr}")
        return "{ " + "; ".join(parts) + " }"
    raise TypeError(f"unsupported type for HOON encoding: {type(v)}")

def json_to_hoon(json_text: str, *, filename: str = "<json>") -> str:
    """
    Convert JSON text -> HOON document text (with {{{ ... }}} root).
    JSON root must be an object (HOON document is always an object).
    """
    try:
        obj = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ParseError(f"{filename}: JSON parse error: {e}") from e

    if not isinstance(obj, dict):
        raise ParseError(f"{filename}: HOON document must be an object (JSON root was {type(obj).__name__})")

    if not obj:
        return "{{{ }}}"

    fields = []
    for k, v in obj.items():
        key_repr = k if is_bare_key(k) else _escape_hoon_string(k)
        val_repr = _encode_hoon_value(v, 0)
        fields.append(f"{key_repr}: {val_repr}")
    body = "; ".join(fields)
    return "{{{ " + body + " }}}"

def hoon_to_json(hoon_text: str, *, filename: str = "<input>", indent: int = 2) -> str:
    """
    Convert HOON document text -> JSON text (strict mapping).
    Parses HOON via hoon.parse, then dumps via json.dumps.
    Comments are dropped, key order preserved, hex -> decimal, text -> string.
    """
    obj = parse(hoon_text, file=filename)
    return json.dumps(obj, indent=indent, ensure_ascii=False)

def hoon_to_json_obj(hoon_text: str, *, filename: str = "<input>") -> Any:
    """Parse HOON and return Python object (dict) suitable for json processing."""
    return parse(hoon_text, file=filename)

def json_to_hoon_obj(json_text: str, *, filename: str = "<json>") -> Any:
    """Parse JSON and return Python object; use json_to_hoon() to get HOON text."""
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ParseError(f"{filename}: JSON parse error: {e}") from e

# Convenience aliases matching potential C++/C API naming
dumps = hoon_to_json
loads = json_to_hoon
