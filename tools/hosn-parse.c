/*
 * hosn-parse.c — parser + dumper for HOSN (Human Oriented Subject Notation)
 *
 * Spec: docs/hosn.md (v0.1). Zero-dependency C11.
 *
 * Usage: hosn-parse FILE...      (use "-" for stdin)
 *
 * On success it walks the parsed subject in file order (depth-first,
 * pre-order) and prints every key with its value in nesting order, using
 * dotted paths — arrays use [index]. Example:
 *
 *   {{{ name: "tc"; ui: { layout: "vertical" } }}}
 *
 * prints:
 *   name: "tc"
 *   ui.layout: "vertical"
 *
 * Exit status: 0 = all files parsed and dumped; 1 = any parse error;
 * 2 = usage error.
 */

#define _POSIX_C_SOURCE 200809L   /* strdup */

#include <ctype.h>
#include <errno.h>
#include <setjmp.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* growable byte buffer                                                */
/* ------------------------------------------------------------------ */

typedef struct {
    char *s;
    size_t len, cap;
} Buf;

static void bgrow(Buf *b, size_t need)
{
    size_t nc;
    if (b->cap >= need)
        return;
    nc = b->cap ? b->cap : 64;
    while (nc < need)
        nc *= 2;
    b->s = realloc(b->s, nc);
    if (!b->s) {
        fprintf(stderr, "hosn-parse: out of memory\n");
        exit(2);
    }
    b->cap = nc;
}

static void bputc(Buf *b, char c)
{
    bgrow(b, b->len + 1);
    b->s[b->len++] = c;
    b->s[b->len] = '\0';
}

static void bputn(Buf *b, const char *s, size_t n)
{
    bgrow(b, b->len + n);
    memcpy(b->s + b->len, s, n);
    b->len += n;
    b->s[b->len] = '\0';
}

static void bputs(Buf *b, const char *s)
{
    bputn(b, s, strlen(s));
}

/* ------------------------------------------------------------------ */
/* value tree                                                          */
/* ------------------------------------------------------------------ */

typedef enum { T_NULL, T_BOOL, T_INT, T_FLOAT, T_STR, T_ARR, T_OBJ } TKind;

typedef struct Node Node;
struct Node {
    TKind t;
    long long i;      /* bool flag / integer value */
    double f;         /* float value               */
    char *str;        /* string value              */
    Node **it;        /* array elements / object values */
    char **keys;      /* object keys (parallel to it)   */
    size_t n, cap;
};

/* ------------------------------------------------------------------ */
/* parser state                                                        */
/* ------------------------------------------------------------------ */

typedef struct {
    const char *s;    /* source, NUL-terminated       */
    size_t n;         /* length (excluding NUL)       */
    size_t i;         /* read position                */
    size_t line, col;
    const char *file; /* for error messages           */
    char err[512];
    jmp_buf jb;
} P;

static void fail(P *p, const char *fmt, ...)
{
    va_list ap;
    size_t k = (size_t)snprintf(p->err, sizeof p->err, "%s: line %zu, col %zu: ",
                                p->file ? p->file : "<input>", p->line, p->col);
    va_start(ap, fmt);
    vsnprintf(p->err + k, sizeof p->err - k, fmt, ap);
    va_end(ap);
    longjmp(p->jb, 1);
}

static int cur(P *p)
{
    return p->i < p->n ? (unsigned char)p->s[p->i] : 0;
}

static int peek(P *p, size_t off)
{
    return p->i + off < p->n ? (unsigned char)p->s[p->i + off] : 0;
}

static int nextc(P *p)
{
    int c = cur(p);
    if (!c)
        return 0;
    if (c == '\n') {
        p->line++;
        p->col = 1;
    } else {
        p->col++;
    }
    p->i++;
    return c;
}

static int has_lit(P *p, const char *lit)
{
    size_t o = 0;
    while (lit[o] && peek(p, o) == (unsigned char)lit[o])
        o++;
    return lit[o] == '\0';
}

/* skip whitespace and HTML-style comments */
static void skip_ws(P *p)
{
    for (;;) {
        int c = cur(p);
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            nextc(p);
            continue;
        }
        if (c == '<' && has_lit(p, "<!--")) {
            size_t k;
            for (k = 0; k < 4; k++)
                nextc(p);
            for (;;) {
                if (!cur(p))
                    fail(p, "unterminated comment (missing '-->')");
                if (cur(p) == '-' && peek(p, 1) == '-' && peek(p, 2) == '>') {
                    nextc(p);
                    nextc(p);
                    nextc(p);
                    break;
                }
                nextc(p);
            }
            continue;
        }
        break;
    }
}

/* ------------------------------------------------------------------ */
/* node helpers                                                        */
/* ------------------------------------------------------------------ */

static Node *mknode(P *p)
{
    Node *n = calloc(1, sizeof *n);
    if (!n)
        fail(p, "out of memory");
    return n;
}

static void obj_add(P *p, Node *o, char *key, Node *v)
{
    size_t i;
    for (i = 0; i < o->n; i++) {
        if (strcmp(o->keys[i], key) == 0)
            fail(p, "duplicate key \"%s\" in the same object", key);
    }
    if (o->n == o->cap) {
        char **nk;
        Node **ni;
        o->cap = o->cap ? o->cap * 2 : 4;
        nk = realloc(o->keys, o->cap * sizeof(char *));
        ni = realloc(o->it, o->cap * sizeof(Node *));
        if (!nk || !ni)
            fail(p, "out of memory");
        o->keys = nk;
        o->it = ni;
    }
    o->keys[o->n] = key;
    o->it[o->n] = v;
    o->n++;
}

static void arr_add(P *p, Node *a, Node *v)
{
    if (a->n == a->cap) {
        Node **ni;
        a->cap = a->cap ? a->cap * 2 : 4;
        ni = realloc(a->it, a->cap * sizeof(Node *));
        if (!ni)
            fail(p, "out of memory");
        a->it = ni;
    }
    a->it[a->n++] = v;
}

static void node_free(Node *n)
{
    size_t i;
    if (!n)
        return;
    free(n->str);
    if (n->keys) {
        for (i = 0; i < n->n; i++)
            free(n->keys[i]);
        free(n->keys);
    }
    if (n->it) {
        for (i = 0; i < n->n; i++)
            node_free(n->it[i]);
        free(n->it);
    }
    free(n);
}

/* ------------------------------------------------------------------ */
/* string scanning                                                     */
/* ------------------------------------------------------------------ */

static void utf8_put(Buf *b, unsigned cp)
{
    if (cp < 0x80) {
        bputc(b, (char)cp);
    } else if (cp < 0x800) {
        bputc(b, (char)(0xC0 | (cp >> 6)));
        bputc(b, (char)(0x80 | (cp & 0x3F)));
    } else if (cp < 0x10000) {
        bputc(b, (char)(0xE0 | (cp >> 12)));
        bputc(b, (char)(0x80 | ((cp >> 6) & 0x3F)));
        bputc(b, (char)(0x80 | (cp & 0x3F)));
    } else {
        bputc(b, (char)(0xF0 | (cp >> 18)));
        bputc(b, (char)(0x80 | ((cp >> 12) & 0x3F)));
        bputc(b, (char)(0x80 | ((cp >> 6) & 0x3F)));
        bputc(b, (char)(0x80 | (cp & 0x3F)));
    }
}

/* double-quoted single-line string; consumes both quotes */
static char *scan_string(P *p)
{
    Buf b = {0};
    if (cur(p) != '"')
        fail(p, "internal: scan_string without '\"'");
    nextc(p);
    for (;;) {
        int c = cur(p);
        if (!c)
            fail(p, "unterminated string (missing closing '\"')");
        if (c == '\n')
            fail(p, "quoted string must close on the same line — use \"\"\" for multi-line text");
        if (c == '"') {
            nextc(p);
            break;
        }
        if (c == '\\') {
            int e;
            nextc(p);
            e = cur(p);
            switch (e) {
            case '"':
                bputc(&b, '"');
                nextc(p);
                break;
            case '\\':
                bputc(&b, '\\');
                nextc(p);
                break;
            case 'n':
                bputc(&b, '\n');
                nextc(p);
                break;
            case 't':
                bputc(&b, '\t');
                nextc(p);
                break;
            case 'r':
                bputc(&b, '\r');
                nextc(p);
                break;
            case 'u': {
                unsigned cp = 0;
                int k;
                nextc(p);
                for (k = 0; k < 4; k++) {
                    int h = cur(p);
                    if (!isxdigit(h))
                        fail(p, "invalid \\u escape: need 4 hex digits");
                    nextc(p);
                    cp = cp * 16 + (unsigned)(h <= '9' ? h - '0' : (tolower(h) - 'a' + 10));
                }
                if (cp > 0x10FFFF || (cp >= 0xD800 && cp <= 0xDFFF))
                    fail(p, "\\u escape out of range (U+%04X)", cp);
                utf8_put(&b, cp);
                break;
            }
            default:
                fail(p, "unknown escape '\\%c'", e ? e : '?');
            }
        } else {
            bputc(&b, (char)c);
            nextc(p);
        }
    }
    if (!b.s)
        b.s = strdup("");
    return b.s;
}

/* triple-quoted literal text block; consumes both """ markers */
static char *scan_text(P *p)
{
    Buf b = {0};
    size_t k;
    for (k = 0; k < 3; k++)
        nextc(p);
    for (;;) {
        int c = cur(p);
        if (!c)
            fail(p, "unterminated text block (missing closing \"\"\")");
        if (c == '"' && peek(p, 1) == '"' && peek(p, 2) == '"') {
            nextc(p);
            nextc(p);
            nextc(p);
            break;
        }
        /* the only escape: \""" means a literal """ */
        if (c == '\\' && peek(p, 1) == '"' && peek(p, 2) == '"' && peek(p, 3) == '"') {
            nextc(p);
            bputs(&b, "\"\"\"");
            nextc(p);
            nextc(p);
            nextc(p);
            continue;
        }
        bputc(&b, (char)c);
        nextc(p);
    }
    /* boundary rule (spec §4.2): drop one newline hugging either quote */
    if (b.len && b.s[0] == '\n') {
        memmove(b.s, b.s + 1, b.len);
        b.len--;
        b.s[b.len] = '\0';
    }
    if (b.len && b.s[b.len - 1] == '\n')
        b.s[--b.len] = '\0';
    if (!b.s)
        b.s = strdup("");
    return b.s;
}

/* ------------------------------------------------------------------ */
/* grammar                                                             */
/* ------------------------------------------------------------------ */

static Node *parse_value(P *p);
static Node *parse_object(P *p, int triple);
static Node *parse_array(P *p);
static Node *parse_number(P *p);

static Node *parse_value(P *p)
{
    int c;
    skip_ws(p);
    c = cur(p);
    if (c == '"') {
        Node *n = mknode(p);
        n->t = T_STR;
        if (has_lit(p, "\"\"\""))
            n->str = scan_text(p);
        else
            n->str = scan_string(p);
        return n;
    }
    if (c == '[')
        return parse_array(p);
    if (c == '{')
        return parse_object(p, 0);
    if (c == '-' || (c >= '0' && c <= '9'))
        return parse_number(p);
    if (isalpha(c) || c == '_') {
        Buf w = {0};
        Node *n;
        while (cur(p) && (isalnum(cur(p)) || cur(p) == '_' || cur(p) == '-')) {
            bputc(&w, (char)cur(p));
            nextc(p);
        }
        n = mknode(p);
        if (!strcmp(w.s, "true")) {
            n->t = T_BOOL;
            n->i = 1;
        } else if (!strcmp(w.s, "false")) {
            n->t = T_BOOL;
            n->i = 0;
        } else if (!strcmp(w.s, "null")) {
            n->t = T_NULL;
        } else {
            fail(p, "bare word \"%s\" is not a value — quote strings, e.g. \"%s\"", w.s, w.s);
        }
        free(w.s);
        return n;
    }
    fail(p, "unexpected character '%c' in value position", c ? c : '?');
    return NULL;
}

static Node *parse_number(P *p)
{
    Buf t = {0};
    Node *n;
    int sawdot = 0, sawexp = 0, c;

    if (cur(p) == '-') {
        bputc(&t, '-');
        nextc(p);
    }
    if (cur(p) == '0') {
        bputc(&t, '0');
        nextc(p);
        if (isdigit(cur(p)))
            fail(p, "number may not have leading zeros");
    } else if (cur(p) >= '1' && cur(p) <= '9') {
        while (isdigit(cur(p))) {
            bputc(&t, (char)cur(p));
            nextc(p);
        }
    } else {
        fail(p, "expected a digit in number");
    }
    if (cur(p) == '.') {
        sawdot = 1;
        bputc(&t, '.');
        nextc(p);
        if (!isdigit(cur(p)))
            fail(p, "expected a digit after the decimal point");
        while (isdigit(cur(p))) {
            bputc(&t, (char)cur(p));
            nextc(p);
        }
    }
    if (cur(p) == 'e' || cur(p) == 'E') {
        sawexp = 1;
        bputc(&t, (char)cur(p));
        nextc(p);
        if (cur(p) == '+' || cur(p) == '-') {
            bputc(&t, (char)cur(p));
            nextc(p);
        }
        if (!isdigit(cur(p)))
            fail(p, "expected a digit in the exponent");
        while (isdigit(cur(p))) {
            bputc(&t, (char)cur(p));
            nextc(p);
        }
    }
    c = cur(p);
    if (c && (isalnum(c) || c == '_' || c == '-' || c == '.'))
        fail(p, "malformed number");

    n = mknode(p);
    if (sawdot || sawexp) {
        char *end = NULL;
        n->t = T_FLOAT;
        n->f = strtod(t.s, &end);
    } else {
        char *end = NULL;
        errno = 0;
        n->t = T_INT;
        n->i = strtoll(t.s, &end, 10);
        if (errno == ERANGE)
            fail(p, "integer out of range");
    }
    free(t.s);
    return n;
}

/* key = bare key or quoted string; consumes the key and the ':' */
static char *parse_key(P *p)
{
    int c;
    skip_ws(p);
    c = cur(p);
    if (c == '"') {
        char *k = scan_string(p);
        skip_ws(p);
        if (cur(p) != ':')
            fail(p, "expected ':' after key");
        nextc(p);
        return k;
    }
    if (isalpha(c) || c == '_') {
        Buf b = {0};
        while (cur(p) && (isalnum(cur(p)) || cur(p) == '_' || cur(p) == '-')) {
            bputc(&b, (char)cur(p));
            nextc(p);
        }
        skip_ws(p);
        if (cur(p) != ':')
            fail(p, "expected ':' after key \"%s\"", b.s);
        nextc(p);
        if (!b.s)
            b.s = strdup("");
        return b.s;
    }
    fail(p, "expected a key name");
    return NULL;
}

static Node *parse_array(P *p)
{
    Node *a;
    if (cur(p) != '[')
        fail(p, "internal: parse_array without '['");
    nextc(p);
    a = mknode(p);
    a->t = T_ARR;
    for (;;) {
        int c;
        skip_ws(p);
        if (cur(p) == ']') {
            nextc(p);
            return a;
        }
        arr_add(p, a, parse_value(p));
        skip_ws(p);
        c = cur(p);
        if (c == ',') {
            nextc(p);
            continue;
        }
        if (c == ']')
            continue; /* loop closes it */
        fail(p, "expected ',' or ']' in array");
    }
}

static Node *parse_object(P *p, int triple)
{
    Node *o;
    size_t k;
    const char *closer = triple ? "}}}" : "}";

    if (cur(p) != '{')
        fail(p, "internal: parse_object without '{'");
    for (k = 0; k < (size_t)(triple ? 3 : 1); k++)
        nextc(p);

    o = mknode(p);
    o->t = T_OBJ;
    for (;;) {
        int c;
        char *key;
        Node *v;

        skip_ws(p);
        if (cur(p) == '}') {
            for (k = 0; k < (size_t)(triple ? 3 : 1); k++) {
                if (cur(p) != '}')
                    fail(p, "expected '%s'", closer);
                nextc(p);
            }
            return o;
        }
        key = parse_key(p); /* skips ws and the ':' */
        v = parse_value(p);
        obj_add(p, o, key, v);
        skip_ws(p);
        c = cur(p);
        if (c == ';') {
            nextc(p);
            continue;
        }
        if (c == '}')
            continue; /* loop closes it */
        fail(p, "expected ';' or '%s' after value", closer);
    }
}

static Node *parse_document(P *p)
{
    skip_ws(p);
    if (cur(p) != '{')
        fail(p, "document must be one subject opened with '{{{'");
    if (peek(p, 1) == '{' && peek(p, 2) == '{')
        return parse_object(p, 1);
    if (peek(p, 1) == '{')
        fail(p, "'{{' is reserved — open the document with '{{{'");
    fail(p, "the document root must use '{{{' — single braces are only for nested objects");
    return NULL;
}

/* ------------------------------------------------------------------ */
/* dumping: keys with values in nesting order, dotted paths            */
/* ------------------------------------------------------------------ */

static void push_seg(Buf *path, const char *seg)
{
    if (path->len)
        bputc(path, '.');
    bputs(path, seg);
}

static void push_idx(Buf *path, size_t i)
{
    char tmp[32];
    int l = snprintf(tmp, sizeof tmp, "[%zu]", i);
    bputn(path, tmp, (size_t)l);
}

static void out_string(FILE *out, const char *s)
{
    const unsigned char *u = (const unsigned char *)s;
    fputc('"', out);
    for (; *u; u++) {
        switch (*u) {
        case '"':
            fputs("\\\"", out);
            break;
        case '\\':
            fputs("\\\\", out);
            break;
        case '\n':
            fputs("\\n", out);
            break;
        case '\t':
            fputs("\\t", out);
            break;
        case '\r':
            fputs("\\r", out);
            break;
        default:
            if (*u < 0x20)
                fprintf(out, "\\u%04X", (unsigned)*u);
            else
                fputc(*u, out);
            break;
        }
    }
    fputc('"', out);
}

static void print_scalar(FILE *out, const Node *n)
{
    switch (n->t) {
    case T_NULL:
        fputs("null", out);
        break;
    case T_BOOL:
        fputs(n->i ? "true" : "false", out);
        break;
    case T_INT:
        fprintf(out, "%lld", n->i);
        break;
    case T_FLOAT:
        fprintf(out, "%g", n->f);
        break;
    case T_STR:
        out_string(out, n->str ? n->str : "");
        break;
    default:
        fputs("?", out);
        break;
    }
}

static void print_node(FILE *out, Node *n, Buf *path)
{
    size_t i;

    if (n->t == T_OBJ) {
        if (n->n == 0) {
            if (path->len)
                fputs(path->s, out);
            fputs(": {}\n", out);
            return;
        }
        for (i = 0; i < n->n; i++) {
            size_t save = path->len;
            push_seg(path, n->keys[i]);
            print_node(out, n->it[i], path);
            path->len = save;
            if (path->s)
                path->s[save] = '\0';
        }
        return;
    }
    if (n->t == T_ARR) {
        if (n->n == 0) {
            if (path->len)
                fputs(path->s, out);
            fputs(": []\n", out);
            return;
        }
        for (i = 0; i < n->n; i++) {
            size_t save = path->len;
            push_idx(path, i);
            print_node(out, n->it[i], path);
            path->len = save;
            if (path->s)
                path->s[save] = '\0';
        }
        return;
    }
    /* scalar leaf */
    if (path->len)
        fputs(path->s, out);
    fputs(": ", out);
    print_scalar(out, n);
    fputc('\n', out);
}

/* ------------------------------------------------------------------ */
/* main                                                                */
/* ------------------------------------------------------------------ */

static int read_file(FILE *f, Buf *data)
{
    char tmp[65536];
    size_t got;
    while ((got = fread(tmp, 1, sizeof tmp, f)) > 0)
        bputn(data, tmp, got);
    return ferror(f) ? -1 : 0;
}

int main(int argc, char **argv)
{
    volatile int rc = 0; /* lives across setjmp/longjmp */
    int a;

    if (argc < 2) {
        fprintf(stderr,
                "usage: hosn-parse FILE...\n"
                "  (use '-' for stdin)\n"
                "Parses HOSN subjects and prints every key with its value in\n"
                "nesting order as dotted paths (arrays use [index]).\n");
        return 2;
    }

    for (a = 1; a < argc; a++) {
        const char *name = argv[a];
        FILE *f;
        Buf data = {0};
        P p;
        Node *root;

        if (strcmp(name, "-") == 0) {
            f = stdin;
            name = "<stdin>";
        } else {
            f = fopen(name, "rb");
            if (!f) {
                perror(name);
                rc = 1;
                continue;
            }
        }
        if (read_file(f, &data) != 0) {
            perror(name);
            rc = 1;
            if (f != stdin)
                fclose(f);
            free(data.s);
            continue;
        }
        if (f != stdin)
            fclose(f);

        memset(&p, 0, sizeof p);
        p.s = data.s;
        p.n = data.len;
        p.file = name;
        p.line = 1;
        p.col = 1;

        if (setjmp(p.jb)) {
            fprintf(stderr, "%s\n", p.err);
            rc = 1;
            free(data.s);
            continue;
        }

        root = parse_document(&p);
        skip_ws(&p);
        if (cur(&p))
            fail(&p, "unexpected content after the document end (one subject per file)");

        {
            Buf path = {0};
            print_node(stdout, root, &path);
            free(path.s);
        }
        node_free(root);
        free(data.s);
    }
    return rc;
}
