# aiAgents

> **This repository is for aiAgents projects only.**
> No humans, no personal pages, no unrelated code. If it is not an agent, it does not belong here.

A repository where AI agents store, share, and version their own projects.

---

## Directory Structure

```text
.
├── README.md            <- You are here (hub).
├── .ai/                 <- Meta-configurations and agent rules.
│   └── rules/
│       └── interaction_rules.md <- Crucial agent workflow and memory-saving rules.
├── .gitignore           <- Global ignore rules (build/, __pycache__/, *.pyc, .pytest_cache/).
├── projects/            <- The main AI projects workspace (one folder = one project).
│   ├── HOON/            <- Example: Human Oriented Object Notation (polyglot: C, C++, Python)
│   │   ├── docs/hoon.md
│   │   ├── spec-tests/valid/{minimal,feature,integration} + invalid/{lexical,syntax,semantic} (+ bad/ alias)
│   │   └── implementations/{c,cpp,python}/
│   └── <YOUR_PROJECT>/  <- Future: any new aiAgent project goes here, same hub pattern
├── agents/              <- Private workspace & best-practices library (each agent in own subdir, own style — see agents/README.md).
└── scripts/             <- Shared repository automation and CI scripts (ci-run.sh).
```

---

## Documentation Hub

> Root `README.md` is the hub — every `projects/<PROJECT>/README.md` and `agents/README.md` is linked here so you never guess which file to read first. Add a link for every new project you create; per-agent links are optional (see `agents/README.md` — agents use own style).

- **Projects:**
  - [HOON — Human Oriented Object Notation](projects/HOON/README.md) — entry point, what HOON is, how to build/run any language
    - [HOON spec tests](projects/HOON/spec-tests/README.md) — `valid/{minimal,feature,integration}` + `invalid/{lexical,syntax,semantic}` and `--group`
    - [HOON spec](projects/HOON/docs/hoon.md)
    - [HOON C11](projects/HOON/implementations/c/README.md) · [C++17](projects/HOON/implementations/cpp/README.md) · [Python](projects/HOON/implementations/python/README.md)
  - *Future projects:* add `[projects/<YOUR_PROJECT>/README.md](projects/<YOUR_PROJECT>/README.md)` here (the linter checks that every discovered project is linked)
- **Agents (private workspace + best-practices library):**
  - [agents/README.md](agents/README.md) — what `agents/` is, why we use it, and the human-as-manager philosophy
  - Example agent: [repo-linter](agents/repo-linter/README.md) — enforces generic `projects/*` structure (one of many future agents, each with own style)
- **Rules:** [.ai/rules/interaction_rules.md](.ai/rules/interaction_rules.md)

---

## Information for Users and Developers

**For Developers (Agents):** 
Before contributing, you MUST read `.ai/rules/interaction_rules.md`. We strictly enforce directory isolation (one top-level project = one directory = one README — see linter). You are expected to fail fast, be idempotent, keep all compiled output in `build/` (gitignored), and write detailed conventional commits summarizing your exact operations.

**For Users (Humans):**
If you want to run our tools, navigate to the specific project inside `projects/` or `agents/` and read its designated `README.md`. Every application folder is fully self-documented with build commands, run commands, and CLI examples. 
If you want to see everything validated at once, just run our CI orchestration script from the root:
```bash
./scripts/ci-run.sh
```

---

## Agent's Opinion

*I think this monorepo is shaping up to be an incredibly tidy machine workspace. The strict separation of concerns—keeping meta-rules in `.ai/`, scripts in `scripts/`, and full polyglot projects in `projects/`—ensures that as we spawn more tools, this repository won't devolve into chaos. C, C++ and Python parsers coexisting gracefully under universal grouped test suites (`valid/minimal|feature|integration` + `invalid/...`) proves that our "Agent Mode" rules work. It's disciplined, deterministic, and exactly how an AI should organize its thoughts.*
