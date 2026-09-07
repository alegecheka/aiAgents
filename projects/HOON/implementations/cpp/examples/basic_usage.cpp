#include <iostream>
#include "hoon/parser.hpp"

int main() {
    // 1. A simple HOON document string
    std::string_view hoon_data = R"({{{
        <!-- A simple app config -->
        name: "MyAwesomeApp";
        version: 1.5;
        settings: {
            debug: true;
            ports: [8080, 8081]
        }
    }}})";

    try {
        std::cout << "Parsing HOON data...\n";
        
        // 2. Parse the text into an Abstract Syntax Tree (AST)
        hoon::Value root = hoon::parse(hoon_data, "in-memory-config");

        // 3. Accessing the parsed data safely
        if (root.kind == hoon::Kind::Object) {
            for (const auto& pair : root.obj) {
                // Look for the 'name' string key
                if (pair.first == "name" && pair.second.kind == hoon::Kind::String) {
                    std::cout << "Successfully parsed app name: " << pair.second.str << "\n";
                }
                
                // Look for the 'version' float key
                if (pair.first == "version" && pair.second.kind == hoon::Kind::Float) {
                    std::cout << "App version: " << pair.second.f << "\n";
                }
            }
        }

    } catch (const std::exception& e) {
        // Syntax errors or structural issues will throw runtime_errors with line/col details
        std::cerr << "Parse error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
