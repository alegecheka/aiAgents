cmake_minimum_required(VERSION 3.14)
project(hoon_cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# The Core Library
add_library(hoon_cpp STATIC src/parser.cpp)
target_include_directories(hoon_cpp PUBLIC include)
target_compile_options(hoon_cpp PRIVATE -Wall -Wextra)

# Executables
add_executable(hoon-parse tools/hoon-parse.cpp)
target_link_libraries(hoon-parse hoon_cpp)

add_executable(hoon-fmt tools/hoon-fmt.cpp)
target_link_libraries(hoon-fmt hoon_cpp)

add_executable(hoon2json tools/hoon2json.cpp)
target_link_libraries(hoon2json hoon_cpp)

# Example Usage
add_executable(basic_usage examples/basic_usage.cpp)
target_link_libraries(basic_usage hoon_cpp)

# Testing
enable_testing()
add_test(
    NAME SpecTests 
    COMMAND bash ${CMAKE_CURRENT_SOURCE_DIR}/tests/run-tests.sh
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
