# HOON C11 Implementation

This is the pure, zero-dependency C11 implementation of the HOON parser.

## How to Build
This project uses a standard Makefile. It builds the `hoon-parse` binary.

```bash
# Build the parser tool
make hoon-parse

# Or build and run the test suite directly
make test
```

## How to Run
The compiled binary `hoon-parse` takes a list of files or accepts input via `stdin`. It will parse the HOON syntax and output the Abstract Syntax Tree as dotted paths.

## Command-Line Examples

Parse a file directly:
```bash
./hoon-parse ../../spec-tests/complex.hoon
```

Parse from standard input:
```bash
echo '{{{ name: "AI Agent"; enabled: true }}}' | ./hoon-parse -
```

*Example Output:*
```text
name: "AI Agent"
enabled: true
```

## Agent's Opinion
*The C11 implementation is brutally fast and beautifully simple. It sets the baseline for the HOON specification. By avoiding external dependencies and using a lightweight recursive descent structure, it guarantees extreme portability. It's the perfect reference implementation.*
