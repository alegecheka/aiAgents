"""hoon.cli.convert — `hoon convert file --to json|hoon`"""
from __future__ import annotations
import sys
from hoon.serializer import hoon_to_json, json_to_hoon
from hoon import ParseError

def run(args, file: str, to: str, indent: int = 2, compact: bool = False) -> int:
    if file == "-":
        data = sys.stdin.read()
        label = "<stdin>"
    else:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = f.read()
        except OSError as e:
            print(f"{file}: {e.strerror}", file=sys.stderr)
            return 1
        label = file
    try:
        if to == "json":
            out = hoon_to_json(data, filename=label, indent=None if compact else indent)
            sys.stdout.write(out + "\n")
        elif to == "hoon":
            out = json_to_hoon(data, filename=label)
            sys.stdout.write(out + "\n")
        else:
            print(f"unknown target: {to} (use json or hoon)", file=sys.stderr)
            return 2
    except ParseError as e:
        print(e, file=sys.stderr)
        return 1
    return 0
