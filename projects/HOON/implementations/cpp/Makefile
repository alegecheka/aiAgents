CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Iinclude

all: hoon-parse hoon-fmt hoon2json

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

test: hoon-parse
	./tests/run-tests.sh

clean:
	rm -rf build hoon-parse hoon-fmt hoon2json

.PHONY: all test clean
