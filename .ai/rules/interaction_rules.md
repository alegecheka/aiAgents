# AI-Agent Interaction Rules

This document outlines the standard rules of engagement when an AI agent works within the `aiAgents` repository. These rules are designed to **save context memory**, **improve project understanding**, and ensure **consistent workflow**.

## 1. Context Memory Preservation
- **Be Concise:** When communicating with the user, keep explanations short and to the point. Avoid conversational filler.
- **Limit Output:** Do not print out the full content of large files (`cat`, `ls -R`, etc.) unless specifically asked. Use tools like `grep`, `head`, `tail`, or read specific chunks to save tokens.
- **Provide Actionable Summaries:** When summarizing a change or command output, only provide the essential details: what failed, what passed, and what was modified.
- **Use Git Diff:** Use `git diff --stat` or show specific diffs instead of outputting the entire updated file content in chat.

## 2. Project Isolation & Understanding
- **One Project, One Directory:** Every individual sub-project (like `HOON`) must live in its own directory with its own `README.md` and build scripts (e.g., `Makefile`).
- **Read First:** When asked to work on an existing project, the AI should always read the project's `README.md` and check its directory structure first before making assumptions.
- **Localized Artifacts:** Any build artifacts, object files, or generated data must be ignored via `.gitignore` at the root or locally inside the project directory.

## 3. Workflow & Actions
- **No Unsolicited Commits (Unless Asked):** Do not commit every single typo fix unless it represents a logical chunk of work.
- **Self-Correction:** Run tests (`make test` or equivalent) after making code changes. If a test fails, fix it before presenting the final result to the user.
- **Commit Messages:** Follow standard conventional commits format (e.g., `feat:`, `fix:`, `chore:`). Additionally, **every commit from an aiAgent must contain a detailed description** in the commit body explaining exactly what was done (e.g., what files were changed, what logic was updated, and how tests were modified).
- **Ask Clarifying Questions:** If a request is ambiguous, surface an interactive question to the user instead of guessing.

## 4. Understanding 'aiAgents' Repositories
- This is a shared space for AI-driven projects.
- The `agents/` folder is reserved for agent-specific code.
- The `scripts/` folder is reserved for shared automation scripts.
- Human intervention should be minimal; the agents write the code, manage the repo, and build the tools.

## 5. Best Practices & Scripting
- **Idempotency:** Scripts and agents should be runnable multiple times without causing unwanted side effects or failures. 
- **Fail Fast:** Scripts in the `scripts/` directory should usually start with `set -euo pipefail` to exit immediately on error. This prevents cascading failures.
- **Self-Documentation (Recommendation):** Documentation is very important, but don't flood with `README.md` in every subfolder. A new agent in `agents/` or project in `projects/` **SHOULD** have a `README.md` if it helps, but the **directory structure itself must make it obvious which README to read first**: `projects/<PROJECT>/README.md` is the entry point for that project (e.g., `projects/HOON/README.md`), `projects/<PROJECT>/spec-tests/README.md` explains tests, `projects/<PROJECT>/implementations/<lang>/README.md` explains that language. The linter enforces structure **generically for any project** in `projects/*` (not just HOON) and does not count READMEs.
- **Use the Environment:** Instead of hardcoding paths, use relative paths intelligently or rely on environment variables (e.g., establishing `$REPO_ROOT` dynamically in bash).

## 6. Documentation Standards
- **Detailed Source Docs (Recommendation):** Documentation is very important, but users must not be confused which `README.md` to read first. The **project directory structure must make it obvious** (generic pattern, HOON as current example):
  - `projects/<PROJECT>/README.md` — entry point: what the project is, how to build/run any part, where tests live (e.g., `projects/HOON/README.md`)
  - `projects/<PROJECT>/spec-tests/README.md` — test layout and grouping (e.g., HOON's `valid/{minimal,feature,integration}` + `invalid/{lexical,syntax,semantic}` and `--group` usage)
  - `projects/<PROJECT>/implementations/<lang>/README.md` — language-specific build/run (where applicable)
  - A top-level `README.md` is **RECOMMENDED** (not hard-required) for a new project/agent if it clarifies; subfolders (`src/`, `tools/`, `tests/`, etc.) should **not** get boilerplate READMEs — they are documented by their parent. The linter **does not** count READMEs; it enforces that the structure itself is clear **generically for any future project** (see `agents/repo-linter/linter.py`).
- **Root README as Hub (Generic):** If a project root `README.md` exists (repo root `README.md` and each `projects/<PROJECT>/README.md`), it **MUST contain explicit markdown links to all of its direct part `README.md` files** so navigation is obvious without guessing. The repo root hub dynamically links to **every** `projects/<PROJECT>/README.md` and **every** `agents/<AGENT>/README.md` discovered in the repo (today e.g., `projects/HOON/README.md`, `projects/HOON/spec-tests/README.md`, `projects/HOON/implementations/c|cpp|python/README.md`, `agents/repo-linter/README.md` — but the rule applies to any future project/agent). Each project hub (`projects/<PROJECT>/README.md`) links to its own parts like `spec-tests/README.md` and each `implementations/<lang>/README.md` (or other sub-component READMEs where they exist). The linter **warns** if these dynamically discovered hub links are missing.
- **Root Readme Scope:** The project root `README.md` should ONLY contain basic information, the directory structure, hub links (above), necessary info for users/developers, and the agent's overarching opinion. It should not contain deep technical build steps for individual projects.

## 7. Chat History Preservation
- **Record Conversations:** All chat conversations between the user and the agent MUST be saved in `agents/<yourModel-yourOrganization-sessionID-yourAnyName>/chat-history.<format-extension>`. The agent **may choose** the format: `html` → `.html`, `markdown` → `.md`, or `plain text` → `.txt` (e.g., `chat-history.md`, `chat-history.txt`, `chat-history.html`). Do **not** keep a duplicate `chat_history.md` (underscore) — `chat-history.*` (hyphen) is the single source of truth; the underscore variant is deprecated.
- **Additional Files:** The session folder MAY contain **up to 9 additional files** the agent deems useful for clarity (e.g., `agent-opinion.txt`, `notes.md`, `summary.html`, diagrams). Do **not** flood with boilerplate `README.md` files — keep it lean. The linter exempts `agents/*session*` folders from the top-level `README.md` requirement; they are log stores, not projects.
- **Purpose:** This ensures context is preserved across long-running engagements and acts as an audit trail of decisions for any future agent.
