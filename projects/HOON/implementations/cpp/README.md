# HOON C++ Implementation

This is a modern C++17 implementation of the HOON (human oriented object notation) parser. It is written with zero external dependencies and compiles into a static library (`libhoon.a`) that can be embedded securely into other projects.

## Architecture
- `include/hoon/` contains the public API (`parser.hpp` and `value.hpp`).
- `src/` contains the core library implementation.
- `tools/` contains standalone executables (like `hoon-parse`) that link against the library.
- `examples/` contains usage examples.

## Building
You can build this library using **CMake** or the provided fallback **Makefile**.

**Using CMake:**
```bash
cmake -B build
cmake --build build
```

**Using Make:**
```bash
make all
```

## Basic Usage Example
Linking against `libhoon` allows you to parse HOON documents directly into a C++ Abstract Syntax Tree (AST). 

Here is how you parse a HOON string in memory (from `examples/basic_usage.cpp`):

```cpp
#include <iostream>
#include "hoon/parser.hpp"

int main() {
    std::string_view hoon_data = R"({{{
        name: "MyAwesomeApp";
        version: 1.5;
        settings: {
            debug: true;
            ports: [8080, 8081]
        }
    }}})";

    try {
        // Parse the text into an Abstract Syntax Tree (AST)
        hoon::Value root = hoon::parse(hoon_data, "in-memory-config");

        if (root.kind == hoon::Kind::Object) {
            for (const auto& pair : root.obj) {
                if (pair.first == "name" && pair.second.kind == hoon::Kind::String) {
                    std::cout << "App name: " << pair.second.str << "\n";
                }
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Parse error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
```

You can compile and run this example directly using the `basic_usage` target:
```bash
make basic_usage
./basic_usage
```
