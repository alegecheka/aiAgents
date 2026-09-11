#!/usr/bin/env python3
"""hoon.cli.main — unified `hoon` dispatcher."""
from __future__ import annotations
import argparse
import sys
from . import parse as cli_parse, convert as cli_convert, format as cli_format, validate as cli_validate

def print_help():
    print("""hoon — HOON toolkit

USAGE:
  hoon <command> [OPTIONS] [FILES]

COMMANDS:
  parse     Parse HOON and dump (default, also hoon file.hoon)
  convert   HOON ⇄ JSON  (hoon convert file --to json|hoon)
  format    Canonical format (hoon format file.hoon --check/--in-place)
  validate  Run spec-tests (hoon validate --group valid/feature)

OPTIONS:
  -h, --help     Show this help
  --version      Show version

EXAMPLES:
  hoon parse spec-tests/valid/feature/numbers.hoon --json
  hoon convert file.hoon --to json
  hoon convert file.json --to hoon
  hoon format file.hoon --check
  hoon validate --group invalid/lexical
""")

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print_help()
        return 0
    if argv[0] in ("--version", "-V"):
        print("hoon 0.1.0 (python)")
        return 0

    cmd = argv[0]
    rest = argv[1:]

    # compat: if first arg is a file (not a command), treat as parse
    if cmd not in ("parse", "convert", "format", "validate") and not cmd.startswith("-"):
        # e.g. `hoon file.hoon` or `hoon --json file`
        # legacy tools/hoon-parse allowed `hoon-parse file` without subcommand
        return cli_parse.run([], [cmd] + rest, to_hoon=False, to_json=False)

    if cmd == "parse":
        p = argparse.ArgumentParser(prog="hoon parse", add_help=False)
        p.add_argument("files", nargs="+", help="Files to parse (use '-' for stdin)")
        p.add_argument("--json", action="store_true", help="Output JSON")
        p.add_argument("--to-hoon", action="store_true", help="JSON→HOON")
        p.add_argument("-h", "--help", action="store_true")
        try:
            ns, unknown = p.parse_known_args(rest)
        except SystemExit as e:
            return e.code
        if ns.help:
            print("""hoon parse — parse HOON and dump

USAGE:
  hoon parse [OPTIONS] <FILES...>

OPTIONS:
  --json     Output JSON (HOON→JSON)
  --to-hoon  Treat input as JSON and output HOON
  -h, --help Show this help
""")
            return 0
        return cli_parse.run(rest, ns.files, to_hoon=ns.to_hoon, to_json=ns.json)

    if cmd == "convert":
        p = argparse.ArgumentParser(prog="hoon convert", add_help=False)
        p.add_argument("file", help="Input file ('-' for stdin)")
        p.add_argument("--to", dest="to", required=True, help="Target: json or hoon")
        p.add_argument("--indent", type=int, default=2)
        p.add_argument("--compact", action="store_true")
        p.add_argument("-h", "--help", action="store_true")
        try:
            ns = p.parse_args(rest)
        except SystemExit as e:
            return e.code
        if ns.help:
            print("""hoon convert — HOON ⇄ JSON

USAGE:
  hoon convert <FILE> --to <json|hoon> [--indent 2] [--compact]
""")
            return 0
        return cli_convert.run(rest, ns.file, ns.to, indent=ns.indent, compact=ns.compact)

    if cmd == "format":
        p = argparse.ArgumentParser(prog="hoon format", add_help=False)
        p.add_argument("files", nargs="+")
        p.add_argument("--check", action="store_true")
        p.add_argument("--in-place", action="store_true")
        p.add_argument("-h", "--help", action="store_true")
        try:
            ns = p.parse_args(rest)
        except SystemExit as e:
            return e.code
        if ns.help:
            print("""hoon format — canonical format

USAGE:
  hoon format [OPTIONS] <FILES...>

OPTIONS:
  --check     Check only (exit 1 if not formatted)
  --in-place  Rewrite files in-place
""")
            return 0
        return cli_format.run(rest, ns.files, check=ns.check, in_place=ns.in_place)

    if cmd == "validate":
        p = argparse.ArgumentParser(prog="hoon validate", add_help=False)
        p.add_argument("--group", dest="group", default=None)
        p.add_argument("-h", "--help", action="store_true")
        try:
            ns = p.parse_args(rest)
        except SystemExit as e:
            return e.code
        if ns.help:
            print("""hoon validate — run spec-tests

USAGE:
  hoon validate [--group <GROUP>]
""")
            return 0
        return cli_validate.run(rest, ns.group)

    print(f"unknown command: {cmd} (use --help)", file=sys.stderr)
    return 2

if __name__ == "__main__":
    sys.exit(main())
