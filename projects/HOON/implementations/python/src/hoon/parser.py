"""hoon.parser — recursive-descent parser.

Consumes Lexer; returns Document (ordered dict).
"""
from __future__ import annotations
from .lexer import Lexer, ParseError
from .ast import Document, doc_from_pairs

class Parser:
    """Thin wrapper around Lexer for field/value/document grammar.

    Kept for backwards compat — new code may instantiate Lexer directly.
    Delegates all scanning to Lexer.
    """
    def __init__(self, s: str, file: str = "<input>"):
        self.lex = Lexer(s, file=file)
        self.s = self.lex.s
        self.file = self.lex.file

    @property
    def i(self): return self.lex.i
    @property
    def line(self): return self.lex.line
    @property
    def col(self): return self.lex.col

    def fail(self, msg: str):
        self.lex.fail(msg)

    def cur(self) -> str: return self.lex.cur()
    def peek(self, off: int) -> str: return self.lex.peek(off)
    def nextc(self) -> str: return self.lex.nextc()
    def has_lit(self, lit: str) -> bool: return self.lex.has_lit(lit)
    def skip_ws(self): return self.lex.skip_ws()
    def scan_string(self) -> str: return self.lex.scan_string()
    def scan_text(self) -> str: return self.lex.scan_text()
    def parse_number(self): return self.lex.scan_number()

    def parse_key(self) -> str:
        self.lex.skip_ws()
        c = self.lex.cur()
        if c == '"':
            k = self.lex.scan_string()
        elif c.isalpha() or c == '_':
            b = []
            while self.lex.cur() and (self.lex.cur().isalnum() or self.lex.cur() in '_-'):
                b.append(self.lex.cur())
                self.lex.nextc()
            k = "".join(b)
        else:
            self.lex.fail("expected a key name")
        self.lex.skip_ws()
        if self.lex.cur() != ':':
            self.lex.fail("expected ':' after key")
        self.lex.nextc()
        return k

    def parse_array(self) -> list:
        self.lex.nextc()
        a = []
        while True:
            self.lex.skip_ws()
            if self.lex.cur() == ']':
                self.lex.nextc()
                return a
            a.append(self.parse_value())
            self.lex.skip_ws()
            c = self.lex.cur()
            if c == ',':
                self.lex.nextc()
                continue
            if c == ']':
                continue
            self.lex.fail("expected ',' or ']' in array")

    def parse_object(self, triple: bool) -> Document:
        for _ in range(3 if triple else 1): self.lex.nextc()
        closer = "}}}" if triple else "}"
        pairs = []
        seen = set()
        while True:
            self.lex.skip_ws()
            if self.lex.cur() == '}':
                for _ in range(3 if triple else 1):
                    if self.lex.cur() != '}':
                        self.lex.fail(f"expected '{closer}'")
                    self.lex.nextc()
                return doc_from_pairs(pairs)
            key = self.parse_key()
            val = self.parse_value()
            if key in seen:
                self.lex.fail(f"duplicate key \"{key}\" in the same object")
            seen.add(key)
            pairs.append((key, val))
            self.lex.skip_ws()
            c = self.lex.cur()
            if c == ';':
                self.lex.nextc()
                continue
            if c == '}':
                continue
            self.lex.fail(f"expected ';' or '{closer}' after value")

    def parse_value(self):
        self.lex.skip_ws()
        c = self.lex.cur()
        if c == '"':
            if self.lex.peek(1) == '"' and self.lex.peek(2) == '"':
                return self.lex.scan_text()
            return self.lex.scan_string()
        if c == '-' or c.isdigit():
            return self.lex.scan_number()
        if c == '[':
            return self.parse_array()
        if c == '{':
            if self.lex.peek(1) == '{':
                self.lex.fail("double braces are reserved")
            return self.parse_object(False)
        if c.isalpha() or c == '_':
            b = []
            while self.lex.cur() and (self.lex.cur().isalnum() or self.lex.cur() in '_-'):
                b.append(self.lex.cur())
                self.lex.nextc()
            w = "".join(b)
            if w == "true": return True
            if w == "false": return False
            if w == "null": return None
            self.lex.fail(f"bare word \"{w}\" is not a value — quote strings, e.g. \"{w}\"")
        self.lex.fail("unexpected character in value position")

    def parse_document(self) -> Document:
        self.lex.skip_ws()
        if self.lex.cur() != '{':
            self.lex.fail("document must be one subject opened with '{{{'")
        if self.lex.peek(1) == '{' and self.lex.peek(2) == '{':
            return self.parse_object(True)
        if self.lex.peek(1) == '{':
            self.lex.fail("'{{' is reserved — open the document with '{{{'")
        self.lex.fail("the document root must use '{{{' — single braces are only for nested objects")


def parse(s: str, file: str = "<input>"):
    p = Parser(s, file)
    root = p.parse_document()
    p.lex.skip_ws()
    if p.lex.cur():
        p.lex.fail("unexpected content after the document end (one subject per file)")
    return root

__all__ = ["Parser", "ParseError", "parse"]
