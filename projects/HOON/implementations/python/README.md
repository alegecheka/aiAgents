# HOON Python Implementation

This is the idiomatic Python 3 reference implementation for the HOON (human oriented object notation) parser. It leverages Python's native types, including `dict` (which preserves order in Python 3.7+), avoiding any external dependencies for the library core. 

## Architecture — logical split (6 modules)
- `pyproject.toml` defines the modern Python build environment.
- `src/hoon/` is split into 6 logical modules:
  ```
  src/hoon/
    __init__.py      # facade — re-exports parse/ParseError + Lexer/Document/Value + serializer
    lexer.py         # Lexer {s,i,line,col,file, skip_ws, scan_string, scan_text, scan_number}
    parser.py        # Parser {lexer, parse_key/array/object/value/document} + parse()
    ast.py           # Document = dict[str, Value] + doc_from_pairs()
    value.py         # Value = None|bool|int|float|str|list|dict + is_bare_key()
    serializer.py    # hoon_to_json / json_to_hoon / _encode_hoon_value / _escape_hoon_string
    cli/
      main.py        # hoon {parse,convert,format,validate} dispatcher
      parse.py       # hoon parse file.hoon [--json|--to-hoon] + dotted dump
      convert.py     # hoon convert file --to json|hoon
      format.py      # hoon format file.hoon [--check|--in-place]
      validate.py    # hoon validate --group valid/feature
  ```
  Old `json.py` and `tools/hoon-parse` monoliths are deleted — see `serializer.py` + `cli/`.
- `tests/` contains `pytest` suites alongside the universal grouped HOON validation runner (`tests/run-tests.sh` now calls `python -m hoon.cli.main`).

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

New unified CLI (split from old `tools/hoon-parse`):

```bash
# parse (dotted dump, like spec-tests golden)
PYTHONPATH=src python -m hoon.cli.main parse ../../../spec-tests/valid/integration/complex.hoon
PYTHONPATH=src python -m hoon.cli.main parse ../../../spec-tests/valid/feature/numbers.hoon --json
echo '{{{ name: "AI Agent"; enabled: true }}}' | PYTHONPATH=src python -m hoon.cli.main parse -

# convert (HOON ⇄ JSON, replaces --json/--to-hoon flags)
PYTHONPATH=src python -m hoon.cli.main convert ../../../spec-tests/valid/integration/torture.hoon --to json | head -n 20
echo '{"name": "AI", "vals": [1,2,3]}' | PYTHONPATH=src python -m hoon.cli.main convert - --to hoon
echo '{"note": "hello\nworld", "my odd key": 1}' | PYTHONPATH=src python -m hoon.cli.main convert - --to hoon

# format (canonical)
PYTHONPATH=src python -m hoon.cli.main format file.hoon --check

# validate (wraps spec-tests)
PYTHONPATH=src python -m hoon.cli.main validate --group valid/feature
```

Legacy `tools/hoon-parse` is kept as a thin shim for CI (`PYTHONPATH=src ./tools/hoon-parse ...` still works).

Run the full test suite:

```bash
make test                          # pytest (3) + universal grouped (33)
PYTHONPATH=src pytest tests/       # only pytest unit tests
PYTHONPATH=src bash tests/run-tests.sh --group=valid/feature  # only feature goldens
PYTHONPATH=src bash tests/run-tests.sh --group=invalid/syntax # only syntax rejects
```

### Basic API Usage
Once installed, the library exposes a clean `parse()` function plus **HOON ↔ JSON** helpers from `serializer.py`:

```python
from hoon import parse, ParseError
from hoon.serializer import hoon_to_json, json_to_hoon
# or: from hoon import hoon_to_json, json_to_hoon

try:
    ast = parse('{{{ name: "AI Agent"; tests: [1, 2, 3] }}}')
    print(ast["name"])
    print(ast["tests"][1])

    # HOON → JSON (strict: text/hex → string/number, comments dropped)
    j = hoon_to_json('{{{ n: 0x2A; note: """hello\nworld""" }}}')
    print(j)  # {"n": 42, "note": "hello\nworld"}

    # JSON → HOON (multiline strings become """ blocks, odd keys quoted)
    hoon = json_to_hoon('{"my odd key": 1, "note": "hello\\nworld"}')
    print(hoon)  # {{{ "my odd key": 1; note: """\nhello\nworld\n""" }}}
    # roundtrip
    assert json.loads(hoon_to_json(hoon)) == json.loads(j)
except ParseError as e:
    print(f"Failed: {e}")

# Low-level split also available:
from hoon.lexer import Lexer
from hoon.ast import Document
from hoon.value import Value, is_bare_key
lex = Lexer('{{{ a: "hi" }}}')
doc: Document = parse('{{{ a: "hi" }}}')
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

All 33 must pass + 8 pytest unit tests (3 parser + 5 json roundtrip: hoon_to_json, json_to_hoon, torture, text block, hex).

## Agent's Opinion

*Splitting the monolith into `lexer | parser | ast | value | serializer | cli` makes the Python port mirror the spec (hoon.md §9) line-for-line: Lexer owns comments/escapes/numbers, Parser owns `document→field→value`, AST/Value are pure types, Serializer is the only place with `json` + `is_bare_key`, CLI is just `argparse` dispatch. No new deps, 100% import-path compatible via `hoon/__init__.py` — `from hoon import parse` still works and `from hoon.serializer import …` replaces `hoon.json`. Python developers can now read one file at a time!*
