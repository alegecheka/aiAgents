# Repo Linter Agent

This is a deterministic agent tool that enforces **project directory structure with focus on test clarification** — not just `README.md` counting.

## What it does

It verifies that the repo is navigable without guessing which README to read first — **generically for any future project**, not just HOON (HOON is the current example):

- `projects/*/` — every discovered project must have a `README.md` (warn if missing); each `projects/<PROJECT>/README.md` must link to its own part READMEs (e.g., `spec-tests/README.md`, `implementations/<lang>/README.md`, `docs/*.md` where they exist) — missing links warn (`⚠️`)
- `projects/HOON/` (example) — when project is HOON, extra checks:
  - `spec-tests/valid/{minimal,feature,integration}` each have `.hoon` goldens with paired `.expected` dumps
  - `spec-tests/invalid/{lexical,syntax,semantic}` each have `.hoon` must-reject cases
  - `spec-tests/README.md` exists (recommended as the test-clarification entry point)
  - `implementations/<lang>/` has a test entry (`Makefile`, `CMakeLists.txt`, or `tests/run-tests.sh`)
- **Generic spec-tests rule:** if any `projects/<PROJECT>/spec-tests/` exists, it should have a `README.md` and not be flat (split into `valid`/`invalid` or similar groups for clarity), and `valid` should have `.expected` dumps
- **Generic implementations rule:** if any `projects/<PROJECT>/implementations/<lang>/` exists, each lang should have a build/test entry and a `README.md`
- **Hub links (generic):** root `README.md` must link to **every** `projects/<PROJECT>/README.md` and to `agents/README.md` (the agents workspace entry point; today `projects/HOON/...` + `agents/README.md`); each project README must link to its descendant READMEs — missing links warn (`⚠️`)
- `agents/` is **private workspace & best-practices library — not linted**: every agent may use its own style and practices (see `agents/README.md`). The linter only checks that `agents/README.md` exists; per-agent `README.md` or code presence is not enforced. Session logs like `agents/<model>-<org>-<session>/chat-history.md` are a convention (see `.ai/rules` §7) but not a hard lint error — agents are free.

`README.md` is **recommended**, not hard-required: if a project's `README.md` is missing, the linter warns (`⚠️`) instead of failing. Structure errors (`valid/minimal` missing, no `.expected` dumps) fail (`❌`). `agents/` is intentionally not controlled.

See `.ai/rules/interaction_rules.md` §5-§7 for the philosophy.

## How to Build
This agent is written in pure Python 3. It has **no external dependencies**, so there is no build step or `pip install` required.

## How to Run
Ensure you have Python 3 installed on your system. You can execute the linter directly from the repository root.

## Command-Line Examples

Run the linter manually to check the repository status:
```bash
./agents/repo-linter/linter.py
```

*Example Output (clean):*
```text
🤖 repo-linter agent waking up... inspecting /home/user/aiAgents
✅ All house rules observed. The repository is tidy!
```

*Example with warnings (missing recommended README but structure ok):*
```text
⚠️  projects/HOON/README.md missing — recommended as entry point
✅ Structure is tidy (with recommendations above)
```

*Example with errors (bad structure):*
```text
❌ I found structural violations:
  - spec-tests/valid/minimal/ missing — add minimal/feature/integration grouping
```

## Agent's Opinion
*Counting `README.md` files was a blunt hammer. Checking that `spec-tests` is split into `valid` vs `invalid` and that each `valid` file has an `.expected` dump is a scalpel — it tells you instantly if tests are actually clarifying anything. This linter now guides agents toward obvious structure, not boilerplate.*
