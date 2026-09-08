CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -Wpedantic
BUILD   ?= build

all: $(BUILD)/hoon-parse

$(BUILD)/hoon-parse: tools/hoon-parse.c
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -o $@ $<

test: $(BUILD)/hoon-parse
	BUILD=$(BUILD) ./tests/run-tests.sh

clean:
	rm -rf $(BUILD)

.PHONY: all test clean
