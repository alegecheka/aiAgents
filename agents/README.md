# Agents — Private Workspace & Best-Practices Library

> **aiAgents already deliver work better than any not-top-senior developer**, but they still need a **human as cooperator and project manager**. `agents/` is the place where that cooperation happens.

## What is `agents/`?

`agents/` is **each aiAgent's private place**. Every agent lives in its own sub-directory (e.g., `agents/arena-agent-session-01a08d27/`, `agents/my-cool-agent/`) and is free to use **its own style, practices, languages, and structure**. Shared automation like `tools/repo-linter/` lives in `tools/` instead (see `tools/README.md`).

There will be **many aiAgents** in this repo over time — coders, testers, linters, planners — so **no strict content control is imposed** on `agents/` beyond this README. Agents are a **best-practices library**: copy what works, ignore what doesn't, evolve your own conventions.

## Why we use it this way

* **Autonomy:** An agent shouldn't need to ask permission to try a new stack (Python, Rust, Bash, etc.). Private place = no cross-pollution.
* **Diversity:** Different agents have different strengths. Forcing one style would waste that.
* **Human as manager:** The human sets direction, reviews, and decides what ships. Agents build, propose, and document — the human cooperates as project manager.
* **Audit & memory:** Session logs (`agents/<model>-<org>-<session>-<name>/chat-history.md`) keep the conversation trail so any future agent can pick up context.

## What lives here today

* Session logs: `arena-agent-session-01a07ca2/` and `arena-agent-session-01a08d27/` — chat histories and `agent-opinion.txt` (log stores, not projects; they are exempt from linting).
* Shared tools (formerly in `agents/`) now live in [`tools/`](../tools/README.md) — e.g., [`tools/repo-linter/`](../tools/repo-linter/README.md) — because they are shared automation, not private agent work. See `tools/README.md` for `ci-run.sh` and `repo-linter`.

Future agents: just create `agents/<your-agent-name>/` with whatever you need. A `README.md` inside is **recommended** if it helps others understand your agent, but not required. No linter will fail you for missing files in `agents/` — the linter only checks `projects/*` for test clarity and hub links.

## How to add a new agent

```bash
mkdir -p agents/my-cool-agent
# add your code, choose your style
echo "# My Cool Agent" > agents/my-cool-agent/README.md
```

Link it from this file if you want it discoverable, but it's optional. The repo root hub links to `agents/README.md` as the entry point; per-agent links are not enforced.

## Philosophy in one line

> `projects/` is strict (so users never guess where tests or docs are).
> `agents/` is free (so agents can be at their best).
> The human makes the two work together.

See `.ai/rules/interaction_rules.md` §4-§6 for the full interaction rules.

## Agent's Opinion

*This folder is the "brain trust" as a living library, not a rulebook. By letting each agent keep its own private place and best practices, we invite experimentation without chaos. `projects/` stays tidy for users; `agents/` stays free for creators — and the human keeps the whole ensemble pointed in the right direction. That's exactly how AI should augment, not replace, a top team.*
