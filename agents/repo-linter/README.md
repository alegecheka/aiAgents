# Repo Linter Agent

This is a deterministic agent tool designed to enforce the core house rules of the `aiAgents` repository.

## What it does
It scans the repository to ensure that every sub-project in `projects/` and every agent in `agents/` conforms to the rule:
> "One agent project = one directory = one README."

If a directory is missing a `README.md`, the linter will complain and exit with a non-zero status.

## Usage
It can be run directly:
```bash
./agents/repo-linter/linter.py
```
Or it is automatically invoked via our Continuous Integration scripts in `scripts/`.
