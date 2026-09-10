# HOON C11 Implementation

This is the pure, zero-dependency C11 implementation of the HOON parser.

## Architecture
- `tools/hoon-parse.c` — standalone parser + dotted-path dumper, links no libs.
- `tests/run-tests.sh` — universal grouped test runner (see Testing below).
- `build/` — all compiled output (`hoon-parse`), gitignored. `BUILD=out` overrides.

## How to Build
This project uses a standard Makefile. It builds the `hoon-parse` binary into `build/`.

```bash
# Build the parser tool
make

# Or build and run the test suite directly (33 tests: 15 valid + 18 invalid)
make test

# Custom build directory
BUILD=out make
BUILD=out make test
```

`make hoon-parse` is an alias for `make build/hoon-parse`. `make clean` removes `build/`.

## How to Run
The compiled binary `hoon-parse` takes a list of files or accepts input via `stdin`. It parses HOON and prints the AST as dotted paths:

* `empty object` → `a: {}`
* `empty array` → `a: []`
* `empty doc` → `: {}` (root empty)
* `object` → `a.b: "val"` (dot), `array` → `a[0]: 1` (bracket)

## Command-Line Examples

Parse a file directly:

```bash
./build/hoon-parse ../../spec-tests/valid/integration/complex.hoon
./build/hoon-parse ../../spec-tests/valid/feature/numbers.hoon
```

Parse from standard input:

```bash
echo '{{{ name: "AI Agent"; enabled: true }}}' | ./build/hoon-parse -
```

Run subgroup tests:

```bash
bash tests/run-tests.sh --group=valid/minimal      # 4 smoke tests
bash tests/run-tests.sh --group=valid/feature      # 8 isolated feature tests
bash tests/run-tests.sh --group=invalid/lexical    # 5 lexical rejects
```

*Example Output:*
```text
name: "AI Agent"
enabled: true
```

## Testing

Universal grouped suite lives in `../../spec-tests/` — see `../../spec-tests/README.md`.

| Group | Count | Run |
|-------|-------|-----|
| valid/minimal | 4 | `--group=valid/minimal` |
| valid/feature | 8 | `--group=valid/feature` |
| valid/integration | 3 | `--group=valid/integration` (torture, mega, complex) |
| invalid/lexical | 5 | `--group=invalid/lexical` |
| invalid/syntax | 10 | `--group=invalid/syntax` |
| invalid/semantic | 3 | `--group=invalid/semantic` |

All 33 must pass. Dotted-path dumps are `diff -u`'d against `*.expected`.

## Agent's Opinion

*The C11 implementation is brutally fast and beautifully simple. It sets the baseline for the HOON specification. By avoiding external dependencies and using a lightweight recursive descent structure, it guarantees extreme portability. It's the perfect reference implementation.*
