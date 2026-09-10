# HOON C++ Implementation

This is a modern C++17 implementation of the HOON (human oriented object notation) parser. It is written with zero external dependencies and compiles into a static library (`libhoon.a`) that can be embedded securely into other projects.

## Architecture
- `include/hoon/` contains the public API (`parser.hpp` and `value.hpp`).
- `src/` contains the core library implementation.
- `tools/` contains standalone executables (like `hoon-parse`) that link against the library (`build/libhoon.a`).
- `examples/` contains usage examples (`basic_usage.cpp`, `stdin_reader.cpp`).
- `tests/run-tests.sh` — universal grouped test runner.

## How to Build
You can build this library using **CMake** or the provided fallback **Makefile**. All output goes to `build/` (gitignored, `BUILD=out` overrides).

**Using CMake:**
```bash
cmake -B build
cmake --build build
```

**Using Make:**
```bash
make all   # outputs go to build/ (hoon-parse, hoon-fmt, hoon2json, basic_usage, stdin_reader, libhoon.a)
make basic_usage  # alias → build/basic_usage
make clean        # removes build/
```

## How to Run & Command-Line Examples

Once built, you can run the parsing tool directly:

```bash
./build/hoon-parse ../../../spec-tests/valid/integration/complex.hoon
./build/hoon-parse ../../../spec-tests/valid/feature/numbers.hoon
```

Run subgroup tests:

```bash
bash tests/run-tests.sh --group=valid/minimal
bash tests/run-tests.sh --group=invalid/syntax
```

### Basic Usage Example
Linking against `libhoon` allows you to parse HOON documents directly into a C++ AST. 

You can compile and run the in-memory parsing example directly:

```bash
make basic_usage
./build/basic_usage
```

### Stdin Reader Example
We also provide `stdin_reader`, which demonstrates how to accept HOON input through a unix pipe (`stdin`), parse it into an AST, and pretty-print it recursively:

```bash
make stdin_reader
echo '{{{ name: "AI Agent"; values: [1, 2.5, false, 0x1A] }}}' | ./build/stdin_reader
```

Via `hoon-parse` stdin as well:

```bash
echo '{{{ name: "AI Agent"; enabled: true }}}' | ./build/hoon-parse -
```

## Testing

Universal grouped suite in `../../../spec-tests/` — see `../../../spec-tests/README.md`.

| Group | Count | Run |
|-------|-------|-----|
| valid/minimal | 4 | `--group=valid/minimal` |
| valid/feature | 8 | `--group=valid/feature` |
| valid/integration | 3 | `torture, mega, complex` |
| invalid/lexical | 5 | `--group=invalid/lexical` |
| invalid/syntax | 10 | `--group=invalid/syntax` |
| invalid/semantic | 3 | `--group=invalid/semantic` |

All 33 must pass. `ctest` (CMake) and `make test` both invoke the same grouped runner.

## Agent's Opinion

*Building this in modern C++17 was highly satisfying. Leveraging `std::variant`, `std::string_view`, and rigorous exceptions makes the library incredibly safe and zero-copy where it counts. Compiling it as a strict static library (`libhoon.a`) ensures it can easily be embedded in larger AI tools without linking nightmares. It represents a mature evolution from the C reference.*
