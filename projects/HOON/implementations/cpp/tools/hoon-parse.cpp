#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "hoon/parser.hpp"

using namespace hoon;

void push_seg(std::string& path, const std::string& seg) {
    if (!path.empty()) path += '.';
    path += seg;
}

void push_idx(std::string& path, size_t i) {
    path += "[" + std::to_string(i) + "]";
}

void out_string(std::ostream& out, const std::string& s) {
    out << '"';
    for (unsigned char c : s) {
        switch (c) {
            case '"': out << "\\\""; break;
            case '\\': out << "\\\\"; break;
            case '\n': out << "\\n"; break;
            case '\t': out << "\\t"; break;
            case '\r': out << "\\r"; break;
            default:
                if (c < 0x20) {
                    char buf[8];
                    snprintf(buf, sizeof(buf), "\\u%04X", c);
                    out << buf;
                } else {
                    out << c;
                }
                break;
        }
    }
    out << '"';
}

void print_scalar(std::ostream& out, const Value& n) {
    switch (n.kind) {
        case Kind::Null: out << "null"; break;
        case Kind::Bool: out << (n.i ? "true" : "false"); break;
        case Kind::Int: out << n.i; break;
        case Kind::Float: out << n.f; break;
        case Kind::String: out_string(out, n.str); break;
        default: out << "?"; break;
    }
}

void print_node(std::ostream& out, const Value& n, std::string& path) {
    if (n.kind == Kind::Object) {
        if (n.obj.empty()) {
            if (!path.empty()) out << path;
            out << ": {}\n";
            return;
        }
        for (const auto& pair : n.obj) {
            size_t save = path.size();
            push_seg(path, pair.first);
            print_node(out, pair.second, path);
            path.resize(save);
        }
        return;
    }
    if (n.kind == Kind::Array) {
        if (n.arr.empty()) {
            if (!path.empty()) out << path;
            out << ": []\n";
            return;
        }
        for (size_t i = 0; i < n.arr.size(); i++) {
            size_t save = path.size();
            push_idx(path, i);
            print_node(out, n.arr[i], path);
            path.resize(save);
        }
        return;
    }
    
    if (!path.empty()) out << path;
    out << ": ";
    print_scalar(out, n);
    out << '\n';
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: hoon-parse FILE...\n"
                  << "  (use '-' for stdin)\n"
                  << "Parses HOON subjects and prints every key with its value in\n"
                  << "nesting order as dotted paths (arrays use [index]).\n";
        return 2;
    }

    int rc = 0;
    for (int a = 1; a < argc; a++) {
        std::string name = argv[a];
        std::string data;
        
        if (name == "-") {
            name = "<stdin>";
            std::ostringstream ss;
            ss << std::cin.rdbuf();
            data = ss.str();
        } else {
            std::ifstream f(name, std::ios::binary);
            if (!f) {
                perror(name.c_str());
                rc = 1;
                continue;
            }
            std::ostringstream ss;
            ss << f.rdbuf();
            data = ss.str();
        }

        try {
            Value root = parse(data, name);
            std::string path;
            print_node(std::cout, root, path);
        } catch (const std::exception& e) {
            std::cerr << e.what() << '\n';
            rc = 1;
        }
    }
    return rc;
}
