"""hoon.cli.parse — `hoon parse file.hoon [--json]`"""
from __future__ import annotations
import sys
from hoon import parse, ParseError
from hoon.serializer import hoon_to_json, json_to_hoon

def out_string(s: str) -> str:
    out = ['"']
    for c in s:
        if c == '"': out.append('\\"')
        elif c == '\\': out.append('\\\\')
        elif c == '\n': out.append('\\n')
        elif c == '\t': out.append('\\t')
        elif c == '\r': out.append('\\r')
        else:
            code = ord(c)
            if code < 0x20:
                out.append(f"\\u{code:04X}")
            else:
                out.append(c)
    out.append('"')
    return "".join(out)

def print_node(n, path: str):
    if isinstance(n, dict):
        if not n:
            if path: sys.stdout.write(path)
            sys.stdout.write(": {}\n")
            return
        for k, v in n.items():
            new_path = f"{path}.{k}" if path else k
            print_node(v, new_path)
        return
    if isinstance(n, list):
        if not n:
            if path: sys.stdout.write(path)
            sys.stdout.write(": []\n")
            return
        for i, v in enumerate(n):
            new_path = f"{path}[{i}]"
            print_node(v, new_path)
        return
    if path: sys.stdout.write(path)
    sys.stdout.write(": ")
    if n is None:
        sys.stdout.write("null\n")
    elif isinstance(n, bool):
        sys.stdout.write("true\n" if n else "false\n")
    elif isinstance(n, int):
        sys.stdout.write(f"{n}\n")
    elif isinstance(n, float):
        sys.stdout.write(f"{n:g}\n")
    elif isinstance(n, str):
        sys.stdout.write(f"{out_string(n)}\n")

def run(args, files, to_hoon: bool, to_json: bool) -> int:
    rc = 0
    for name in files:
        if name == "-":
            data = sys.stdin.read()
            label = "<stdin>"
        else:
            try:
                with open(name, "r", encoding="utf-8") as f:
                    data = f.read()
            except OSError as e:
                print(f"{name}: {e.strerror}", file=sys.stderr)
                rc = 1
                continue
            label = name
        try:
            if to_hoon:
                out = json_to_hoon(data, filename=label)
                sys.stdout.write(out + "\n")
            elif to_json:
                out = hoon_to_json(data, filename=label, indent=2)
                sys.stdout.write(out + "\n")
            else:
                root = parse(data, file=label)
                print_node(root, "")
        except ParseError as e:
            print(e, file=sys.stderr)
            rc = 1
        except Exception as e:
            print(f"{label}: {e}", file=sys.stderr)
            rc = 1
    return rc
