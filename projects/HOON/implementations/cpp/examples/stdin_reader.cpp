#include <iostream>
#include <sstream>
#include "hoon/parser.hpp"

// A simple recursive function to print the HOON AST
void print_ast(const hoon::Value& val, int indent = 0) {
    std::string pad(indent, ' ');
    switch (val.kind) {
        case hoon::Kind::Null: 
            std::cout << "null"; 
            break;
        case hoon::Kind::Bool: 
            std::cout << (val.i ? "true" : "false"); 
            break;
        case hoon::Kind::Int: 
            std::cout << val.i; 
            break;
        case hoon::Kind::Float: 
            std::cout << val.f; 
            break;
        case hoon::Kind::String: 
            std::cout << '"' << val.str << '"'; 
            break;
        case hoon::Kind::Array:
            std::cout << "[\n";
            for (const auto& item : val.arr) {
                std::cout << pad << "  ";
                print_ast(item, indent + 2);
                std::cout << ",\n";
            }
            std::cout << pad << "]";
            break;
        case hoon::Kind::Object:
            std::cout << "{\n";
            for (const auto& pair : val.obj) {
                std::cout << pad << "  " << pair.first << ": ";
                print_ast(pair.second, indent + 2);
                std::cout << ",\n";
            }
            std::cout << pad << "}";
            break;
    }
}

int main() {
    // Read all contents from standard input into a string
    std::ostringstream ss;
    ss << std::cin.rdbuf();
    std::string input = ss.str();

    if (input.empty()) {
        std::cerr << "No input provided. Please pipe HOON content to this app.\n";
        std::cerr << "Example: echo '{{{ name: \"test\" }}}' | ./stdin_reader\n";
        return 1;
    }

    try {
        // Parse the input string
        hoon::Value root = hoon::parse(input, "<stdin>");
        
        // Print the parsed AST
        print_ast(root);
        std::cout << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Parse error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
