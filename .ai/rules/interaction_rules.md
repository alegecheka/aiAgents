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
- **Self-Documentation:** Any new agent placed in `agents/` or project in `projects/` must include its own `README.md`.
- **Use the Environment:** Instead of hardcoding paths, use relative paths intelligently or rely on environment variables (e.g., establishing `$REPO_ROOT` dynamically in bash).

## 6. Documentation Standards
- **Detailed Source Docs:** Every folder containing application sources or scripts MUST contain a detailed `README.md`. This README must explicitly include:
  - How to build the project/script.
  - How to run it.
  - Command-line examples.
  - The AI agent's opinion or perspective on the implementation.
- **Root Readme Scope:** The project root `README.md` should ONLY contain basic information, the directory structure, necessary info for users/developers, and the agent's overarching opinion. It should not contain deep technical build steps for individual projects.

## 7. Chat History Preservation
- **Record Conversations:** All chat conversations between the user and the agent MUST be saved in `agents/<yourModel-yourOrganization-sessionID-yourAnyName>/chat_history.md`. This ensures context is preserved across long running engagements and acts as an audit trail of decisions.
