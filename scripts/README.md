# Automation Scripts

This folder contains shared repository automation and Continuous Integration (CI) scripts.

## How to Build
These are pure Bash scripts. No compilation or building is required. Ensure they have executable permissions (`chmod +x scripts/*.sh`).

## How to Run
Scripts should be executed from the root of the repository so they can dynamically resolve `$REPO_ROOT` and interact with all subdirectories properly.

## Command-Line Examples

Run the complete CI orchestration suite (which triggers linters and polyglot tests):

```bash
./scripts/ci-run.sh
```

Run a single implementation's grouped tests directly:

```bash
# All 33 tests for one language
make -C projects/HOON/implementations/c test
# Only feature goldens or only lexical rejects
bash projects/HOON/implementations/c/tests/run-tests.sh --group=valid/feature
bash projects/HOON/implementations/c/tests/run-tests.sh --group=invalid/lexical
# Python needs PYTHONPATH
PYTHONPATH=projects/HOON/implementations/python/src bash projects/HOON/implementations/python/tests/run-tests.sh --group=valid/minimal
```

CI details: `ci-run.sh` scans `projects/HOON/implementations/*/`; if `CMakeLists.txt` is present **and** `cmake` is installed it runs `cmake -B build && cmake --build build && ctest`, otherwise it falls back to `make test`. In minimal sandboxes where `cmake` is absent (like this one), C++ falls back to `make test` — still runs the same 33 grouped tests.

*Example Output:*
```text
======================================
🤖 Starting CI orchestration script...
======================================

==> 1. Running repo-linter agent...
✅ All house rules observed.

==> 2. Running project tests...
--> Testing HOON Implementation: cpp
...
✅ CI Completed Successfully! Agents are happy.
```

## Agent's Opinion
*Bash glue is the unsung hero of any monorepo. `ci-run.sh` dynamically scans for `Makefile` or `CMakeLists.txt` files and seamlessly bridges our polyglot environments. It allows an agent to just type one command and know with absolute certainty if they broke something across the C, C++, or agent tools ecosystems.*
