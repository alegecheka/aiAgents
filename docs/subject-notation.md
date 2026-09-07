# SubjectNotation — Rules v0.1

A human-readable data notation for documents, subjects and files.
Like JSON, but written for people first and parsers second.

Status: **draft for discussion**. Nothing here is final until we say it is.

---

## 0. Design principles

1. Human readability is the top priority.
2. A parser must stay simple — no cleverness that requires a compiler to understand.
3. Anything humans write will contain comments — so HTML-style comments are first-class.
4. Key names are not quoted. Ever. (Quoted keys are an escape hatch, not a style.)
5. Whitespace and indentation carry **no meaning**. Structure comes only from
   braces, separators and quotes.
6. There is exactly one way to write any given thing.

---

## 1. Document and file

- A **file** contains exactly one **document** (also called a **subject**).
  Nothing before it, nothing after it (only whitespace/comments).
- A document is written in **triple braces**:

```text
{{{
  ...
}}}
```

- The triple-brace form is used **only** for the document root.
  Everything nested inside is a plain object in **single braces** `{ ... }`.
- Double braces `{{ ... }}` are **reserved** and are an error in v0.1.
- Recommended file extension: `.subject`
- Encoding: UTF-8. No BOM.
- Key order inside an object is preserved by the parser. Order has no meaning
  unless an application decides it does.

---

## 2. Objects

An **object** is a list of fields inside braces. The document root is an object
in triple braces; nested objects use single braces.

```text
ui: {
  layout: "vertical";
  theme: { color: "#111" }
}
```

Rules:

- Fields are separated by `;`.
- A trailing `;` before the closing brace is optional.
- An object may be empty: `{ }` and `{{{ }}}` are legal.
- Objects nest to any depth.
- A newline or indent is never a separator — if you removed all of them, the
  document would still mean the same thing.

---

## 3. Fields, keys, values

A **field** is `key : value` followed (unless it is the last) by `;`.

### 3.1 Keys

Unquoted keys use a plain charset:

```ebnf
bareKey = [A-Za-z_] ( [A-Za-z0-9_-] )*
```

Examples of legal keys: `name`, `textColor`, `some_field`, `button-2`, `_private`.

If a key must contain anything else (a space, a dot, a digit first), quote it:

```text
"my odd key": "still works";
```

### 3.2 Values

A value is one of:

| kind     | written as                          | example                     |
|----------|-------------------------------------|-----------------------------|
| string   | double quotes                       | `"hello"`                   |
| text     | triple quotes (multi-line)          | `"""line 1\nline 2"""`      |
| integer  | decimal                             | `-42`                       |
| float    | decimal with fraction / exponent    | `3.14`, `1e9`, `-2.5E-3`    |
| boolean  | `true` / `false`                    | `true`                      |
| null     | `null`                              | `null`                      |
| array    | `[ ... ]`                           | `["a", "b", 3]`             |
| object   | `{ ... }`                           | `{ x: 1 }`                  |

**Bare words are never values.** `mode: auto` is an error — write `mode: "auto"`.
This one rule kills an entire class of YAML-style ambiguity.

---

## 4. Strings

### 4.1 Quoted strings (single line)

Double quotes only. Supported escapes:

| escape   | meaning                |
|----------|------------------------|
| `\"`     | double quote           |
| `\\`     | backslash              |
| `\n`     | newline                |
| `\t`     | tab                    |
| `\r`     | carriage return        |
| `\uXXXX` | unicode code point     |

Any other `\x` is an error. A string must close on the same line it opened on
(use a text block for anything longer).

### 4.2 Text blocks (multi-line, triple quotes)

For long or multiline text:

```text
note: """
First line.
Second line, with "quotes" and \ backslashes inside — all literal.
  Leading spaces are kept exactly as written.
"""
```

Rules:

- The block opens with `"""` after the `:` and closes at the next `"""`.
- Inside a text block **everything is literal**: newlines, backslashes, quotes,
  spaces — no escape processing at all. Content is taken exactly as written,
  nothing is trimmed.
- The one exception: to write a literal `"""` inside text, use `\"""`.
- The closing `"""` must be followed by the end of the field (then `;` or the
  closing brace).

---

## 5. Numbers

Plain decimal only, optionally signed:

```ebnf
number = '-'? digits ('.' digits)? (('e' | 'E') ('+' | '-')? digits)?
```

- `0`, `-7`, `42`, `3.14`, `-0.5`, `1e9`, `6.02E23`
- No hex, octal, binary, `Infinity`, `NaN` or leading `+` in v0.1.
- `-0` is `0`. A float with empty fraction (`1.`) is an error.

---

## 6. Arrays

Comma-separated values in square brackets:

```text
buttons: ["invert text color", "default", "get agent note"];
```

Rules:

- Elements are separated by `,`.
- A trailing comma is optional: `["a", "b",]` is legal.
- Elements may be any value type, mixed freely, nested freely: `[1, "two", { three: 3 }, [4]]`.
- An array may be empty: `[]`.

---

## 7. Comments

HTML-style comments — the **only** allowed comment form:

```text
<!-- this is a comment -->
```

Rules:

- `//` and `/* */` are **not** comments. They are errors.
- A comment may span multiple lines.
- A comment may appear anywhere whitespace is allowed: between fields, between
  a key and `:`, inside an array, even inside an otherwise-empty object.
- Comments are whitespace to a parser: they are ignored, not preserved.
  (Preserving them is a possible v0.2 feature, if we want round-trips.)
- An unclosed comment is an error.

---

## 8. Duplicate keys

Duplicate keys inside the same object are an **error**. Strict and predictable.
Merging and overriding are not the parser's job.

---

## 9. Grammar (EBNF)

```ebnf
(* lexical *)
ws         = { whitespace | comment };        (* ignorable *)
comment    = "<!--" { any except "-->" } "-->";
bareKey    = [A-Za-z_] { [A-Za-z0-9_-] };
string     = '"' { char | escape } '"';
text       = '"""' { rawchar } '"""';          (* rawchar: literal; \""" -> """ *)
escape     = '\"' | '\\' | '\n' | '\t' | '\r' | '\u' hex hex hex hex;
number     = '-'? digit { digit } ['.' { digit }] [('e'|'E') ['+'|'-'] digit { digit }];
bool       = 'true' | 'false';
null       = 'null';

(* structure *)
document   = ws '{{{' ws body? ws '}}}' ws;   (* then end of file *)
object     = ws '{' ws body? ws '}';
array      = ws '[' ws [ value { ws ',' ws value } [ ws ',' ] ] ws ']';
value      = string | text | number | bool | null | array | object;
field      = ( bareKey | string ) ws ':' ws value;
body       = field { ws ';' ws field } [ ws ';' ];
```

---

## 10. Canonical style (for generated files)

Not required — but when a tool *writes* `.subject` files it SHOULD use:

- 2-space indent per nesting level;
- unquoted keys wherever the charset allows;
- no trailing `;` on the last field of an object;
- `;` after every field except the last;
- arrays written `[a, b, c]` with one space after each comma;
- a blank line between top-level fields when the document is long.

Example document (canonical form):

```text
{{{<!-- text converter app definition -->
  name: "text-converter";
  version: 1.2;
  ui: {
    layout: "vertical";
    buttons: ["invert text color", "default", "get agent note"];
    buttonStyle: {
      color: "#111";
      background: "#eee"
    }
  };
  input: {
    label: "original text";
    placeholder: "type here..."
  };
  output: {
    label: "converted text"
  };
  about: """
An example that demonstrates SubjectNotation v0.1.
Backslashes and "quotes" are literal in text blocks.
\""" the only escape: three quotes in a row.
"""
}}}
```

---

## 11. Common errors (a parser must reject these)

| you write                          | why                                       |
|------------------------------------|-------------------------------------------|
| `mode: auto`                       | bare word value — quote it                |
| `a: 1 b: 2`                        | missing `;` between fields                |
| `key "value"`                      | missing `:`                               |
| `x: "unterminated`                 | unterminated string                       |
| `x: """abc`                        | unterminated text block                   |
| `x: /* nope */`                    | only HTML-style comments exist            |
| `{a: 1}; {b: 2}` after `}}}`       | content after the document root           |
| `x: 1; x: 2`                       | duplicate key                             |
| `n: 01` or `f: 1.`                 | bad number                                |
| `{{ anything }}`                   | double braces are reserved                |

---

## 12. Open questions (v0.2 candidates — not decided)

- Embedded subjects: allow `{{{ }}}` documents nested inside documents?
- `include` / `import` directives between files?
- Preserving comments on parse (round-trip support)?
- Hex (`0x1F`) and binary numbers?
- Multi-document files separated by a marker?
- Type directives / schema validation?
- Anything you want to add — this list is yours.
