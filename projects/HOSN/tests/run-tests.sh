#!/usr/bin/env bash
# HOSN parser test suite.
#   1. Golden test: tests/complex.hosn must parse and its dump (keys with
#      values in nesting order) must match tests/complex.expected byte for byte.
#   2. Negative tests: every tests/bad/*.hosn must be rejected.
set -u

root="$(cd "$(dirname "$0")/.." && pwd)"
bin="$root/hosn-parse"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

pass=0
failn=0
ok()   { printf 'PASS  %s\n' "$1"; pass=$((pass + 1)); }
bad()  { printf 'FAIL  %s\n' "$1"; failn=$((failn + 1)); }

# --- golden test ---------------------------------------------------------
if "$bin" "$root/tests/complex.hosn" > "$tmp/complex.out" 2> "$tmp/complex.err"; then
    if diff -u "$root/tests/complex.expected" "$tmp/complex.out" > "$tmp/complex.diff"; then
        ok "complex.hosn parses; golden dump matches"
    else
        bad "complex.hosn: dump differs from golden (diff below)"
        sed 's/^/    /' "$tmp/complex.diff" | head -60
    fi
else
    bad "complex.hosn: parser rejected it (expected success)"
    sed 's/^/    /' "$tmp/complex.err" | head -10
fi

# --- negative tests -------------------------------------------------------
for f in "$root"/tests/bad/*.hosn; do
    name="$(basename "$f")"
    if "$bin" "$f" > /dev/null 2>&1; then
        bad "$name: parser ACCEPTED it (expected rejection)"
    else
        ok "$name: rejected as expected"
    fi
done

printf '\n%d passed, %d failed\n' "$pass" "$failn"
[ "$failn" -eq 0 ]
