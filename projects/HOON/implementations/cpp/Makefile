CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Iinclude
AR       ?= ar

all: hoon-parse hoon-fmt hoon2json

# The Core Library
build/libhoon.a: build/parser.o
	@mkdir -p build
	$(AR) rcs $@ $^

build/parser.o: src/parser.cpp
	@mkdir -p build
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Executables
hoon-parse: tools/hoon-parse.cpp build/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -Lbuild -lhoon

hoon-fmt: tools/hoon-fmt.cpp build/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -Lbuild -lhoon

hoon2json: tools/hoon2json.cpp build/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -Lbuild -lhoon

test: hoon-parse
	./tests/run-tests.sh

clean:
	rm -rf build hoon-parse hoon-fmt hoon2json

.PHONY: all test clean
