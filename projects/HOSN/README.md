# HOSN (Human Oriented Subject Notation)

HOSN is a data format that looks like JSON and YAML had a child, but with simpler syntax geared towards readability. 

## Structure
- `docs/` contains the HOSN spec.
- `tools/` contains the C parser (`hosn-parse.c`).
- `tests/` contains tests for the parser.

## Usage
To build the parser and run tests:
```bash
make test
```
