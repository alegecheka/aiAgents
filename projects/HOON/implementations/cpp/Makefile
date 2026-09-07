CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Iinclude

all: hoon-parse hoon-fmt hoon2json test_runner

# Library object
build/parser.o: src/parser.cpp
	@mkdir -p build
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Executables
hoon-parse: tools/hoon-parse.cpp build/parser.o
	$(CXX) $(CXXFLAGS) -o $@ $^

hoon-fmt: tools/hoon-fmt.cpp build/parser.o
	$(CXX) $(CXXFLAGS) -o $@ $^

hoon2json: tools/hoon2json.cpp build/parser.o
	$(CXX) $(CXXFLAGS) -o $@ $^

test_runner: tests/test_runner.cpp build/parser.o
	$(CXX) $(CXXFLAGS) -o $@ $^

test: test_runner
	./test_runner

clean:
	rm -rf build hoon-parse hoon-fmt hoon2json test_runner

.PHONY: all test clean
