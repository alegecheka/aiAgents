#pragma once
#include "value.hpp"
#include <string_view>
#include <string>

namespace hoon {
    Value parse(std::string_view input, const std::string& filename = "<input>");
}
