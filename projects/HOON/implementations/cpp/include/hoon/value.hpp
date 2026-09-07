#pragma once
#include <string>
#include <vector>
#include <stdexcept>

namespace hoon {
    enum class Kind { Null, Bool, Int, Float, String, Array, Object };

    struct Value {
        Kind kind;
        long long i = 0;
        double f = 0.0;
        std::string str;
        std::vector<Value> arr;
        std::vector<std::pair<std::string, Value>> obj;

        Value() : kind(Kind::Null) {}
        Value(bool b) : kind(Kind::Bool), i(b ? 1 : 0) {}
        Value(long long v) : kind(Kind::Int), i(v) {}
        Value(double v) : kind(Kind::Float), f(v) {}
        Value(const std::string& v) : kind(Kind::String), str(v) {}
        Value(Kind k) : kind(k) {}
    };
}
