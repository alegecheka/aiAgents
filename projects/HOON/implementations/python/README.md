# HOON Python Implementation

This is the idiomatic Python 3 reference implementation for the HOON (human oriented object notation) parser. It leverages Python's native types, including `dict` (which preserves order in Python 3.7+), avoiding any external dependencies for the library core. 

## Architecture
- `pyproject.toml` defines the modern Python build environment.
- `src/hoon/` contains the `Parser` implementation (`parser.py`).
- `tools/hoon-parse` is the command-line script to evaluate HOON sources.
- `tests/` contains `pytest` suites alongside the universal grouped HOON validation runner (`tests/run-tests.sh`).

## How to Build
This package is structured to be installed cleanly using modern python tooling:
```bash
pip install .
```

For development and running tests, install with dev dependencies:
```bash
pip install -e .[dev]
```

No separate compile step — `src/` is used directly via `PYTHONPATH=src`.

## How to Run & Command-Line Examples

To test the parser locally, you can use the `hoon-parse` tool. Since it reads the local `src/hoon` directory if you haven't installed it system-wide, you can run:

```bash
PYTHONPATH=src ./tools/hoon-parse ../../../spec-tests/valid/integration/complex.hoon
PYTHONPATH=src ./tools/hoon-parse ../../../spec-tests/valid/feature/numbers.hoon
echo '{{{ name: "AI Agent"; enabled: true }}}' | PYTHONPATH=src ./tools/hoon-parse -
```

Run the full test suite:

```bash
make test                          # pytest (3) + universal grouped (33)
PYTHONPATH=src pytest tests/       # only pytest unit tests
PYTHONPATH=src bash tests/run-tests.sh --group=valid/feature  # only feature goldens
PYTHONPATH=src bash tests/run-tests.sh --group=invalid/syntax # only syntax rejects
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

All 33 must pass + 3 pytest unit tests.

## Agent's Opinion

*Python is arguably the most readable implementation of HOON. Leveraging Python's native `dict` to preserve key insertion order makes constructing the AST trivial and highly Pythonic without any auxiliary maps. Relying on standard tools like `pyproject.toml` and `pytest` ensures the project behaves like a modern package and easily plugs into cross-language validation suites. Python developers can now parse HOON natively!*
