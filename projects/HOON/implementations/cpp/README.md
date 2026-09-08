# HOON C++ Implementation

This is a modern C++17 implementation of the HOON (human oriented object notation) parser. It is written with zero external dependencies and compiles into a static library (`libhoon.a`) that can be embedded securely into other projects.

## Architecture
- `include/hoon/` contains the public API (`parser.hpp` and `value.hpp`).
- `src/` contains the core library implementation.
- `tools/` contains standalone executables (like `hoon-parse`) that link against the library.
- `examples/` contains usage examples.

## How to Build
You can build this library using **CMake** or the provided fallback **Makefile**.

**Using CMake:**
```bash
cmake -B build
cmake --build build
```

**Using Make:**
```bash
make all   # outputs go to build/
```

## How to Run & Command-Line Examples

Once built, you can run the parsing tool directly to evaluate HOON files:
```bash
./build/hoon-parse ../../../spec-tests/complex.hoon
```

### Basic Usage Example
Linking against `libhoon` allows you to parse HOON documents directly into a C++ Abstract Syntax Tree (AST). 

You can compile and run the in-memory parsing example directly using the `basic_usage` target:
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

## Agent's Opinion
*Building this in modern C++17 was highly satisfying. Leveraging `std::variant`, `std::string_view`, and rigorous exceptions makes the library incredibly safe and zero-copy where it counts. Compiling it as a strict static library (`libhoon.a`) ensures it can easily be embedded in larger AI tools without linking nightmares. It represents a mature evolution from the C reference.*
