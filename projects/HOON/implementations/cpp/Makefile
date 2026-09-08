CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Iinclude
AR       ?= ar
BUILD    ?= build

BINS := hoon-parse hoon-fmt hoon2json basic_usage stdin_reader

all: $(addprefix $(BUILD)/,$(BINS))

# The Core Library
$(BUILD)/libhoon.a: $(BUILD)/parser.o
	$(AR) rcs $@ $^

$(BUILD)/parser.o: src/parser.cpp
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Executables
$(BUILD)/hoon-parse: tools/hoon-parse.cpp $(BUILD)/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -L$(BUILD) -lhoon

$(BUILD)/hoon-fmt: tools/hoon-fmt.cpp $(BUILD)/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -L$(BUILD) -lhoon

$(BUILD)/hoon2json: tools/hoon2json.cpp $(BUILD)/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -L$(BUILD) -lhoon

$(BUILD)/basic_usage: examples/basic_usage.cpp $(BUILD)/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -L$(BUILD) -lhoon

$(BUILD)/stdin_reader: examples/stdin_reader.cpp $(BUILD)/libhoon.a
	$(CXX) $(CXXFLAGS) -o $@ $< -L$(BUILD) -lhoon

# Convenience aliases: `make hoon-parse` builds build/hoon-parse
$(BINS): %: $(BUILD)/%

test: $(BUILD)/hoon-parse
	./tests/run-tests.sh

clean:
	rm -rf $(BUILD)

.PHONY: all test clean $(BINS)
