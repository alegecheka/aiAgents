#include "hoon/parser.hpp"
#include <cctype>
#include <cmath>
#include <charconv>

namespace hoon {

struct ParserState {
    std::string_view s;
    size_t i = 0;
    size_t line = 1;
    size_t col = 1;
    std::string file;

    [[noreturn]] void fail(const std::string& msg) {
        throw std::runtime_error(file + ": line " + std::to_string(line) + ", col " + std::to_string(col) + ": " + msg);
    }

    int cur() const { return i < s.size() ? static_cast<unsigned char>(s[i]) : 0; }
    int peek(size_t off) const { return i + off < s.size() ? static_cast<unsigned char>(s[i + off]) : 0; }
    
    int nextc() {
        int c = cur();
        if (!c) return 0;
        if (c == '\n') { line++; col = 1; } else { col++; }
        i++;
        return c;
    }

    bool has_lit(const std::string_view& lit) {
        if (i + lit.size() > s.size()) return false;
        return s.substr(i, lit.size()) == lit;
    }

    void skip_ws() {
        while (true) {
            int c = cur();
            if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
                nextc();
                continue;
            }
            if (c == '<' && has_lit("<!--")) {
                for (int k = 0; k < 4; k++) nextc();
                while (true) {
                    if (!cur()) fail("unterminated comment (missing '-->')");
                    if (cur() == '-' && peek(1) == '-' && peek(2) == '>') {
                        nextc(); nextc(); nextc();
                        break;
                    }
                    nextc();
                }
                continue;
            }
            break;
        }
    }

    void utf8_put(std::string& b, unsigned cp) {
        if (cp < 0x80) {
            b.push_back(static_cast<char>(cp));
        } else if (cp < 0x800) {
            b.push_back(static_cast<char>(0xC0 | (cp >> 6)));
            b.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
        } else if (cp < 0x10000) {
            b.push_back(static_cast<char>(0xE0 | (cp >> 12)));
            b.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
            b.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
        } else {
            b.push_back(static_cast<char>(0xF0 | (cp >> 18)));
            b.push_back(static_cast<char>(0x80 | ((cp >> 12) & 0x3F)));
            b.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
            b.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
        }
    }

    std::string scan_string() {
        if (cur() != '"') fail("internal: scan_string without '\"'");
        nextc();
        std::string b;
        while (true) {
            int c = cur();
            if (!c) fail("unterminated string (missing closing '\"')");
            if (c == '\n') fail("quoted string must close on the same line — use \"\"\" for multi-line text");
            if (c == '"') {
                nextc();
                break;
            }
            if (c == '\\') {
                nextc();
                int e = cur();
                switch (e) {
                case '"': b.push_back('"'); nextc(); break;
                case '\\': b.push_back('\\'); nextc(); break;
                case 'n': b.push_back('\n'); nextc(); break;
                case 't': b.push_back('\t'); nextc(); break;
                case 'r': b.push_back('\r'); nextc(); break;
                case 'u': {
                    unsigned cp = 0;
                    nextc();
                    for (int k = 0; k < 4; k++) {
                        int h = cur();
                        if (!std::isxdigit(h)) fail("invalid \\u escape: need 4 hex digits");
                        nextc();
                        cp = cp * 16 + (h <= '9' ? h - '0' : (std::tolower(h) - 'a' + 10));
                    }
                    if (cp > 0x10FFFF || (cp >= 0xD800 && cp <= 0xDFFF)) fail("\\u escape out of range");
                    utf8_put(b, cp);
                    break;
                }
                default: fail(std::string("unknown escape '\\") + static_cast<char>(e ? e : '?') + "'");
                }
            } else {
                b.push_back(static_cast<char>(c));
                nextc();
            }
        }
        return b;
    }

    std::string scan_text() {
        std::string b;
        for (int k = 0; k < 3; k++) nextc();
        while (true) {
            int c = cur();
            if (!c) fail("unterminated text block (missing closing \"\"\")");
            if (c == '"' && peek(1) == '"' && peek(2) == '"') {
                nextc(); nextc(); nextc();
                break;
            }
            if (c == '\\' && peek(1) == '"' && peek(2) == '"' && peek(3) == '"') {
                nextc(); b += "\"\"\""; nextc(); nextc(); nextc();
                continue;
            }
            b.push_back(static_cast<char>(c));
            nextc();
        }
        if (!b.empty() && b.front() == '\n') b.erase(0, 1);
        if (!b.empty() && b.back() == '\n') b.pop_back();
        return b;
    }

    Value parse_number() {
        std::string t;
        bool sawdot = false, sawexp = false, is_hex = false;

        if (cur() == '-') { t.push_back('-'); nextc(); }
        
        if (cur() == '0') {
            t.push_back('0'); nextc();
            if (cur() == 'x' || cur() == 'X') {
                is_hex = true;
                t.push_back(cur()); nextc();
                if (!std::isxdigit(cur())) fail("expected a hex digit after 0x");
                while (std::isxdigit(cur())) { t.push_back(cur()); nextc(); }
            } else if (std::isdigit(cur())) {
                fail("number may not have leading zeros");
            }
        } else if (cur() >= '1' && cur() <= '9') {
            while (std::isdigit(cur())) { t.push_back(cur()); nextc(); }
        } else {
            fail("expected a digit in number");
        }
        
        if (!is_hex) {
            if (cur() == '.') {
                sawdot = true;
                t.push_back('.'); nextc();
                if (!std::isdigit(cur())) fail("expected a digit after the decimal point");
                while (std::isdigit(cur())) { t.push_back(cur()); nextc(); }
            }
            
            if (cur() == 'e' || cur() == 'E') {
                sawexp = true;
                t.push_back(cur()); nextc();
                if (cur() == '+' || cur() == '-') { t.push_back(cur()); nextc(); }
                if (!std::isdigit(cur())) fail("expected a digit in the exponent");
                while (std::isdigit(cur())) { t.push_back(cur()); nextc(); }
            }
        }
        
        int c = cur();
        if (c && (std::isalnum(c) || c == '_' || c == '-' || c == '.')) fail("malformed number");

        if (sawdot || sawexp) {
            return Value(std::stod(t));
        } else {
            try {
                return Value(std::stoll(t, nullptr, is_hex ? 16 : 10));
            } catch(...) {
                fail("integer out of range");
            }
        }
    }

    std::string parse_key() {
        skip_ws();
        int c = cur();
        std::string k;
        if (c == '"') {
            k = scan_string();
        } else if (std::isalpha(c) || c == '_') {
            while (cur() && (std::isalnum(cur()) || cur() == '_' || cur() == '-')) {
                k.push_back(cur());
                nextc();
            }
        } else {
            fail("expected a key name");
        }
        skip_ws();
        if (cur() != ':') fail("expected ':' after key");
        nextc();
        return k;
    }

    Value parse_value();

    Value parse_array() {
        nextc();
        Value a(Kind::Array);
        while (true) {
            skip_ws();
            if (cur() == ']') { nextc(); return a; }
            a.arr.push_back(parse_value());
            skip_ws();
            int c = cur();
            if (c == ',') { nextc(); continue; }
            if (c == ']') continue;
            fail("expected ',' or ']' in array");
        }
    }

    Value parse_object(int triple) {
        for (int k = 0; k < (triple ? 3 : 1); k++) nextc();
        Value o(Kind::Object);
        std::string closer = triple ? "}}}" : "}";

        while (true) {
            skip_ws();
            if (cur() == '}') {
                for (int k = 0; k < (triple ? 3 : 1); k++) {
                    if (cur() != '}') fail("expected '" + closer + "'");
                    nextc();
                }
                return o;
            }
            std::string key = parse_key();
            Value v = parse_value();
            
            for (const auto& pair : o.obj) {
                if (pair.first == key) fail("duplicate key \"" + key + "\" in the same object");
            }
            o.obj.push_back({key, std::move(v)});
            
            skip_ws();
            int c = cur();
            if (c == ';') { nextc(); continue; }
            if (c == '}') continue;
            fail("expected ';' or '" + closer + "' after value");
        }
    }

    Value parse_document() {
        skip_ws();
        if (cur() != '{') fail("document must be one subject opened with '{{{'");
        if (peek(1) == '{' && peek(2) == '{') return parse_object(1);
        if (peek(1) == '{') fail("'{{' is reserved — open the document with '{{{'");
        fail("the document root must use '{{{' — single braces are only for nested objects");
    }
};

Value ParserState::parse_value() {
    skip_ws();
    int c = cur();
    if (c == '"') {
        if (peek(1) == '"' && peek(2) == '"') return Value(scan_text());
        return Value(scan_string());
    }
    if (c == '-' || std::isdigit(c)) return parse_number();
    if (c == '[') return parse_array();
    if (c == '{') {
        if (peek(1) == '{') fail("double braces are reserved");
        return parse_object(0);
    }
    if (std::isalpha(c) || c == '_') {
        std::string w;
        while (cur() && (std::isalnum(cur()) || cur() == '_' || cur() == '-')) {
            w.push_back(cur());
            nextc();
        }
        if (w == "true") return Value(true);
        if (w == "false") return Value(false);
        if (w == "null") return Value(Kind::Null);
        fail("bare word \"" + w + "\" is not a value — quote strings, e.g. \"" + w + "\"");
    }
    fail("unexpected character in value position");
}

Value parse(std::string_view input, const std::string& filename) {
    ParserState p{input, 0, 1, 1, filename};
    Value root = p.parse_document();
    p.skip_ws();
    if (p.cur()) p.fail("unexpected content after the document end (one subject per file)");
    return root;
}

} // namespace hoon
