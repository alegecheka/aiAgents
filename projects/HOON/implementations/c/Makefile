CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -Wpedantic

hoon-parse: tools/hoon-parse.c
	$(CC) $(CFLAGS) -o $@ $<

test: hoon-parse
	./tests/run-tests.sh

clean:
	rm -f hoon-parse

.PHONY: test clean
