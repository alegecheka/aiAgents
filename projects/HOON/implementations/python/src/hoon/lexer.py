"""hoon.lexer — low-level scanning.

Extracted from the original monolithic parser.py. Owns all character-level
logic: whitespace/comments, strings, texts, numbers. Parser consumes Lexer.
"""
from __future__ import annotations
import string

class ParseError(Exception):
    pass

class Lexer:
    def __init__(self, s: str, file: str = "<input>"):
        self.s = s
        self.i = 0
        self.line = 1
        self.col = 1
        self.file = file

    def fail(self, msg: str):
        raise ParseError(f"{self.file}: line {self.line}, col {self.col}: {msg}")

    def cur(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def peek(self, off: int) -> str:
        return self.s[self.i + off] if self.i + off < len(self.s) else ""

    def nextc(self) -> str:
        c = self.cur()
        if not c:
            return ""
        if c == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.i += 1
        return c

    def has_lit(self, lit: str) -> bool:
        return self.s.startswith(lit, self.i)

    def skip_ws(self):
        while True:
            c = self.cur()
            if not c:
                break
            if c in " \t\r\n":
                self.nextc()
                continue
            if c == '<' and self.has_lit("<!--"):
                for _ in range(4): self.nextc()
                while True:
                    if not self.cur():
                        self.fail("unterminated comment (missing '-->')")
                    if self.cur() == '-' and self.peek(1) == '-' and self.peek(2) == '>':
                        for _ in range(3): self.nextc()
                        break
                    self.nextc()
                continue
            break

    def scan_string(self) -> str:
        if self.cur() != '"':
            self.fail("internal: scan_string without '\"'")
        self.nextc()
        b = []
        while True:
            c = self.cur()
            if not c:
                self.fail("unterminated string (missing closing '\"')")
            if c == '\n':
                self.fail("quoted string must close on the same line — use \"\"\" for multi-line text")
            if c == '"':
                self.nextc()
                break
            if c == '\\':
                self.nextc()
                e = self.cur()
                if e == '"': b.append('"'); self.nextc()
                elif e == '\\': b.append('\\'); self.nextc()
                elif e == 'n': b.append('\n'); self.nextc()
                elif e == 't': b.append('\t'); self.nextc()
                elif e == 'r': b.append('\r'); self.nextc()
                elif e == 'u':
                    self.nextc()
                    cp = 0
                    for _ in range(4):
                        h = self.cur()
                        if h not in string.hexdigits:
                            self.fail("invalid \\u escape: need 4 hex digits")
                        self.nextc()
                        cp = cp * 16 + int(h, 16)
                    if cp > 0x10FFFF or (0xD800 <= cp <= 0xDFFF):
                        self.fail(f"\\u escape out of range")
                    b.append(chr(cp))
                else:
                    self.fail(f"unknown escape '\\{e or '?'}'")
            else:
                b.append(c)
                self.nextc()
        return "".join(b)

    def scan_text(self) -> str:
        for _ in range(3): self.nextc()
        b = []
        while True:
            c = self.cur()
            if not c:
                self.fail("unterminated text block (missing closing \"\"\"") 
            if c == '"' and self.peek(1) == '"' and self.peek(2) == '"':
                for _ in range(3): self.nextc()
                break
            if c == '\\' and self.peek(1) == '"' and self.peek(2) == '"' and self.peek(3) == '"':
                self.nextc()
                b.append('"""')
                for _ in range(3): self.nextc()
                continue
            b.append(c)
            self.nextc()
        text = "".join(b)
        if text.startswith('\n'): text = text[1:]
        if text.endswith('\n'): text = text[:-1]
        return text

    def scan_number(self):
        t = []
        sawdot = False
        sawexp = False
        is_hex = False

        if self.cur() == '-':
            t.append('-')
            self.nextc()

        if self.cur() == '0':
            t.append('0')
            self.nextc()
            if self.cur() in ('x', 'X'):
                is_hex = True
                t.append(self.cur())
                self.nextc()
                if not (self.cur() and self.cur() in string.hexdigits):
                    self.fail("expected a hex digit after 0x")
                while self.cur() and self.cur() in string.hexdigits:
                    t.append(self.cur())
                    self.nextc()
            elif self.cur() and self.cur().isdigit():
                self.fail("number may not have leading zeros")
        elif self.cur() and self.cur().isdigit():
            while self.cur() and self.cur().isdigit():
                t.append(self.cur())
                self.nextc()
        else:
            self.fail("expected a digit in number")

        if not is_hex:
            if self.cur() == '.':
                sawdot = True
                t.append('.')
                self.nextc()
                if not (self.cur() and self.cur().isdigit()):
                    self.fail("expected a digit after the decimal point")
                while self.cur() and self.cur().isdigit():
                    t.append(self.cur())
                    self.nextc()

            if self.cur() in ('e', 'E'):
                sawexp = True
                t.append(self.cur())
                self.nextc()
                if self.cur() in ('+', '-'):
                    t.append(self.cur())
                    self.nextc()
                if not (self.cur() and self.cur().isdigit()):
                    self.fail("expected a digit in the exponent")
                while self.cur() and self.cur().isdigit():
                    t.append(self.cur())
                    self.nextc()

        c = self.cur()
        if c and (c.isalnum() or c in '_-.'):
            self.fail("malformed number")

        num_str = "".join(t)
        if sawdot or sawexp:
            return float(num_str)
        else:
            try:
                return int(num_str, 16 if is_hex else 10)
            except ValueError:
                self.fail("integer out of range")
