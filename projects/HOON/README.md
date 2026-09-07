# HOON (human oriented object notation)

HOON is a data format that looks like JSON and YAML had a child, but with simpler syntax geared towards readability. 

## Structure
- `docs/` contains the HOON spec.
- `tools/` contains the C parser (`hoon-parse.c`).
- `tests/` contains tests for the parser.

## Usage
To build the parser and run tests:
```bash
make test
```
