# HOON (human oriented object notation)

HOON is a data format that looks like JSON and YAML had a child, but with simpler syntax geared towards readability. 

## Structure
- `docs/` contains the HOON specification (`hoon.md`).
- `spec-tests/` contains the universal, cross-language test suites:
  - `valid/minimal/` (4) — smallest legal docs
  - `valid/feature/` (8) — one feature per file (numbers, strings, texts, keys, arrays, objects, comments, scalars)
  - `valid/integration/` (3) — combined stress documents (`complex`, `torture`, `mega`)
  - `invalid/lexical|syntax|semantic/` (18) — must-reject cases
  - `bad/` — legacy alias to `invalid/` (kept 1 week)
  - See `spec-tests/README.md` for the full table and `--group` usage.
- `implementations/` contains the actual parsers written in different languages (C, C++, Python).

## How to Build

Each implementation builds independently into `build/` (gitignored):

| Implementation | Build |
|----------------|-------|
| C (C11) | `cd implementations/c && make` → `build/hoon-parse` |
| C++ (C++17) | `cd implementations/cpp && make all` or `cmake -B build && cmake --build build` → `build/hoon-parse`, `build/libhoon.a` |
| Python | `cd implementations/python && pip install -e .[dev]` (or just `PYTHONPATH=src` for dev) |

## How to Run

```bash
# Per-language (from its folder)
make test                          # all 33 tests (15 valid + 18 invalid)
bash tests/run-tests.sh --group=valid/feature   # only feature goldens
bash tests/run-tests.sh --group=invalid/lexical # only lexical rejects

# All languages at once (from repo root)
./scripts/ci-run.sh
```

*Note: See the individual `README.md` files inside `implementations/c/`, `implementations/cpp/`, and `implementations/python/` for detailed language-specific instructions and CLI examples.*

## Command-Line Examples

Run a single golden file through any parser:

```bash
./implementations/c/build/hoon-parse spec-tests/valid/feature/numbers.hoon
./implementations/cpp/build/hoon-parse spec-tests/valid/integration/torture.hoon
PYTHONPATH=implementations/python/src ./implementations/python/tools/hoon-parse spec-tests/valid/minimal/single-field.hoon
```

Run the universal test suite across ALL implementations at once from the root:

```bash
# Run from the aiAgents root directory
./scripts/ci-run.sh
```

## Agent's Opinion

*Grouping tests into `valid/minimal|feature|integration` and `invalid/lexical|syntax|semantic` was the next masterstroke after extracting `spec-tests/` itself. Isolated feature files pinpoint bugs in seconds, while `torture`/`mega` prove the parsers survive real-world stress. The new `--group` flag turns a 33-test sledgehammer into a scalpel — exactly the kind of hierarchy a polyglot monorepo needs to stay sane as we add Rust or Go.*
