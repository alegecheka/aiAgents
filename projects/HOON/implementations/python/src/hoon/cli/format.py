"""hoon.cli.format — `hoon format file.hoon [--check] [--in-place]`"""
from __future__ import annotations
import sys
from hoon import parse, ParseError
from hoon.serializer import json_to_hoon, hoon_to_json

def run(args, files, check: bool, in_place: bool) -> int:
    rc = 0
    for name in files:
        try:
            with open(name, "r", encoding="utf-8") as f:
                data = f.read()
        except OSError as e:
            print(f"{name}: {e.strerror}", file=sys.stderr)
            rc = 1
            continue
        try:
            # canonical format via parse -> json_to_hoon(hoon_to_json(...)) to ensure §10
            obj = parse(data, file=name)
            # Use serializer to produce canonical HOON
            import json
            j = json.dumps(obj, ensure_ascii=False)
            formatted = json_to_hoon(j, filename=name)
            formatted_nl = formatted + "\n"
            if check:
                if formatted_nl != data and formatted != data:
                    print(f"{name}: not formatted", file=sys.stderr)
                    rc = 1
            elif in_place:
                if formatted_nl != data:
                    with open(name, "w", encoding="utf-8") as out:
                        out.write(formatted_nl)
            else:
                sys.stdout.write(formatted + "\n")
        except ParseError as e:
            print(e, file=sys.stderr)
            rc = 1
    return rc
