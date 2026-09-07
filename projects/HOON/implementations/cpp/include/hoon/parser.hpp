#pragma once
#include "value.hpp"
#include <string_view>
#include <stdexcept>

namespace hoon {
    // Throws std::runtime_error on failure
    Value parse(std::string_view input);
}
