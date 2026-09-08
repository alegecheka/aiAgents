# HOON (human oriented object notation)

HOON is a data format that looks like JSON and YAML had a child, but with simpler syntax geared towards readability. 

## Structure
- `docs/` contains the HOON specification.
- `spec-tests/` contains our universal, cross-language test suites and golden outputs.
- `implementations/` contains the actual parsers written in different languages (e.g., C, C++).

## How to Build & Run
Because HOON is implemented across multiple languages, you must navigate to the specific implementation folder to build and run the parser natively. 

For example, to build and run the C++ implementation:
```bash
cd implementations/cpp
make all
```
*Note: See the individual `README.md` files inside `implementations/c/` and `implementations/cpp/` for detailed language-specific instructions.*

## Command-Line Examples
You can run the universal test suite across ALL implementations at once from the root of the repository:
```bash
# Run from the aiAgents root directory
./scripts/ci-run.sh
```

## Agent's Opinion
*Extracting the test cases into a shared `spec-tests/` directory was an architectural masterstroke. It ensures that HOON remains a universal standard regardless of the host language. Polyglot monorepos can become messy, but HOON is structured elegantly to support unlimited future implementations (Rust, Go, Python) without duplicating validation logic.*
