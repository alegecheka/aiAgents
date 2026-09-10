# HOON Spec Tests

Universal, cross-language test suite for the HOON specification. Every parser (C, C++, Python) must pass these tests byte-identically.

## Structure

```text
spec-tests/
├── valid/                     # Must parse — golden files with .expected dumps
│   ├── minimal/   (4)        # Smallest legal docs
│   │   ├── empty-doc.hoon        → ": {}"
│   │   ├── empty-object.hoon     → "a: {}"
│   │   ├── empty-array.hoon      → "a: []"
│   │   └── single-field.hoon     → "name: \"minimal\""
│   ├── feature/   (8)        # One feature per file — pinpoints bug
│   │   ├── numbers.hoon      # 0, -0, hex 0x/0X, floats, exps
│   │   ├── strings.hoon      # escapes \" \\ \n \t \r \uXXXX + utf8
│   │   ├── texts.hoon        # empty, indented, triple-escaped
│   │   ├── keys.hoon         # bare vs quoted ("my odd key")
│   │   ├── arrays.hoon       # trailing comma, nested, matrix3d
│   │   ├── objects.hoon      # deep, trailing ;, comments
│   │   ├── comments.hoon     # comments in every position
│   │   └── scalars.hoon      # bool/null + mixed
│   └── integration/ (3)      # Combined — real-world stress
│       ├── complex.hoon      # original golden (50 lines)
│       ├── torture.hoon      # exhaustive edge torture (102 lines)
│       └── mega.hoon         # galactic outpost config (91 lines)
└── invalid/                  # Must reject — no .expected
    ├── lexical/   (5)        # Tokenization failures
    │   └── bad-escape, slash-comment, unterminated-{comment,string,text}
    ├── syntax/   (10)        # Grammar violations
    │   └── dot-number, double-braces, exp-number, leading-zero,
    │       missing-colon, missing-semi-array, missing-semi,
    │       multiline-string, single-brace-root, trailing-content
    └── semantic/   (3)       # Valid grammar, wrong meaning
        └── duplicate, bare-word, bare-word-trueish
└── bad/          (18)        # Legacy alias — same 18 files flat, kept 1 week
```

`15 valid` (4+8+3) + `18 invalid` = **33 tests**. Valid files have paired `.expected` dumps; invalid files have only `.hoon` (must fail).

## How to Run

From any implementation directory:

```bash
# All 33 tests
make test
# or directly
bash tests/run-tests.sh

# Subgroups (new --group filter)
bash tests/run-tests.sh --group=valid/minimal        # 4
bash tests/run-tests.sh --group=valid/feature        # 8  (numbers, strings...)
bash tests/run-tests.sh --group=valid/integration    # 3  (torture, mega, complex)
bash tests/run-tests.sh --group=valid                # 15 (all valid)
bash tests/run-tests.sh --group=invalid/lexical      # 5
bash tests/run-tests.sh --group=invalid/syntax       # 10
bash tests/run-tests.sh --group=invalid/semantic     # 3
bash tests/run-tests.sh --group=invalid              # 18
bash tests/run-tests.sh --group=lexical              # bare name also works
bash tests/run-tests.sh --group=bad                  # alias → invalid (18)
```

From repo root, validate all languages at once:

```bash
./tools/ci-run.sh
```

Each parser dumps to dotted paths (`a.b[0]: "val"`) and `diff -u` compares to `.expected`. All three implementations must be byte-identical.

## Command-Line Examples

Test a single golden file manually:

```bash
# C
./projects/HOON/implementations/c/build/hoon-parse projects/HOON/spec-tests/valid/feature/numbers.hoon
# C++ (Make)
./projects/HOON/implementations/cpp/build/hoon-parse projects/HOON/spec-tests/valid/integration/torture.hoon
# Python
PYTHONPATH=projects/HOON/implementations/python/src ./projects/HOON/implementations/python/tools/hoon-parse projects/HOON/spec-tests/valid/minimal/single-field.hoon
```

Test an invalid file (must exit 1):

```bash
./projects/HOON/implementations/c/build/hoon-parse projects/HOON/spec-tests/invalid/syntax/dot-number.hoon; echo $?
# → 1 + error: "invalid/lexical/dot-number.hoon: line 1, col X: ..."
```

## Agent's Opinion

*Grouping by intent (minimal → feature → integration, lexical/syntax/semantic) is a game-changer. When `valid/feature/numbers.hoon` fails, you know it's number parsing, not a tangled integration bug. Keeping `bad/` as an alias for a week gives us safe migration without breaking old CI. The `--group` flag turns a 33-test sledgehammer into a scalpel.*
