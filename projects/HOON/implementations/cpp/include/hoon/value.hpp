#pragma once
#include <string>
#include <variant>
#include <vector>
#include <map>

namespace hoon {
    struct Null {};
    using Value = std::variant<Null, bool, double, std::string>; // simplified stub for scaffolding
}
