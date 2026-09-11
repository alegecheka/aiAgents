"""hoon.cli.validate — `hoon validate [--group valid/feature]`"""
from __future__ import annotations
import subprocess
import sys
import pathlib

def run(args, group: str | None) -> int:
    root = pathlib.Path(__file__).resolve().parents[3]  # implementations/python
    script = root / "tests" / "run-tests.sh"
    cmd = ["bash", str(script)]
    if group:
        cmd.append(f"--group={group}")
    result = subprocess.run(cmd)
    return result.returncode
