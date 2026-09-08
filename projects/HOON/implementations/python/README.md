# HOON Python Implementation

This is the idiomatic Python 3 reference implementation for the HOON (human oriented object notation) parser. It leverages Python's native types, including `dict` (which preserves order in Python 3.7+), avoiding any external dependencies for the library core. 

## Architecture
- `pyproject.toml` defines the modern Python build environment.
- `src/hoon/` contains the `Parser` implementation.
- `tools/hoon-parse` is the command-line script to evaluate HOON sources.
- `tests/` contains `pytest` suites alongside the universal HOON validation runner.

## How to Build
This package is structured to be installed cleanly using modern python tooling:
```bash
pip install .
```

For development and running tests, install with dev dependencies:
```bash
pip install -e .[dev]
```

## How to Run & Command-Line Examples

To test the parser locally, you can use the `hoon-parse` tool. Since it reads the local `src/hoon` directory if you haven't installed it system-wide, you can run:

```bash
PYTHONPATH=src ./tools/hoon-parse ../../../spec-tests/complex.hoon
```

### Basic API Usage
Once installed, the library exposes a clean `parse()` function:

```python
from hoon import parse, ParseError

try:
    ast = parse('{{{ name: "AI Agent"; tests: [1, 2, 3] }}}')
    print(ast["name"])
    print(ast["tests"][1])
except ParseError as e:
    print(f"Failed: {e}")
```

## Agent's Opinion
*Python is arguably the most readable implementation of HOON. Leveraging Python's native `dict` to preserve key insertion order makes constructing the AST trivial and highly Pythonic without any auxiliary maps. Relying on standard tools like `pyproject.toml` and `pytest` ensures the project behaves like a modern package and easily plugs into cross-language validation suites. Python developers can now parse HOON natively!*
