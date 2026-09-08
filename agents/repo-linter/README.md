# Repo Linter Agent

This is a deterministic agent tool designed to enforce the core house rules of the `aiAgents` repository.

## What it does
It scans the repository to ensure that every sub-project in `projects/` and every agent in `agents/` conforms to the strict documentation rule:
> "One agent project = one directory = one README."

If a directory is missing a `README.md`, the linter will complain and exit with a non-zero status.

## How to Build
This agent is written in pure Python 3. It has **no external dependencies**, so there is no build step or `pip install` required.

## How to Run
Ensure you have Python 3 installed on your system. You can execute the linter directly from the repository root.

## Command-Line Examples

Run the linter manually to check the repository status:
```bash
./agents/repo-linter/linter.py
```

*Example Output:*
```text
🤖 repo-linter agent waking up... inspecting /home/user/aiAgents
✅ All house rules observed. The repository is tidy!
```

## Agent's Opinion
*This linter is a fantastic first line of defense. By having a simple, dependency-free Python script enforce our structural rules, we guarantee that no sloppy AI (or human) commits an undocumented folder. It's lightweight, fast, and integrates perfectly into our CI bash scripts.*
