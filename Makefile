CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -Wpedantic

hosn-parse: tools/hosn-parse.c
	$(CC) $(CFLAGS) -o $@ $<

test: hosn-parse
	./tests/run-tests.sh

clean:
	rm -f hosn-parse

.PHONY: test clean
