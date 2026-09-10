#!/usr/bin/env bash
# HOON parser test suite (C implementation).
#   1. Golden tests: every spec-tests/*.hoon with matching *.expected must parse and dump-match
#   2. Negative tests: every spec-tests/bad/*.hoon must be rejected.
set -u

root="$(cd "$(dirname "$0")/.." && pwd)"
spec="$(cd "$root/../../spec-tests" && pwd)"
bin="$root/${BUILD:-build}/hoon-parse"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

pass=0; failn=0
ok()   { printf 'PASS  %s\n' "$1"; pass=$((pass + 1)); }
bad()  { printf 'FAIL  %s\n' "$1"; failn=$((failn + 1)); }

# --- golden tests ---------------------------------------------------------
found_golden=0
for exp in "$spec"/*.expected; do
    [ -e "$exp" ] || continue
    found_golden=1
    base=$(basename "$exp" .expected)
    hoon="$spec/$base.hoon"
    if [ ! -f "$hoon" ]; then
        bad "$base: missing .hoon for .expected"
        continue
    fi
    if "$bin" "$hoon" > "$tmp/$base.out" 2> "$tmp/$base.err"; then
        if diff -u "$exp" "$tmp/$base.out" > "$tmp/$base.diff"; then
            ok "$base.hoon parses; golden dump matches"
        else
            bad "$base.hoon: dump differs from golden (diff below)"
            sed 's/^/    /' "$tmp/$base.diff" | head -60
        fi
    else
        bad "$base.hoon: parser rejected it (expected success)"
        sed 's/^/    /' "$tmp/$base.err" | head -10
    fi
done
if [ "$found_golden" -eq 0 ]; then
    bad "no golden files found in $spec"
fi

# --- negative tests -------------------------------------------------------
for f in "$spec"/bad/*.hoon; do
    name="$(basename "$f")"
    if "$bin" "$f" > /dev/null 2>&1; then
        bad "$name: parser ACCEPTED it (expected rejection)"
    else
        ok "$name: rejected as expected"
    fi
done

printf "\n%d passed, %d failed\n" "$pass" "$failn"
[ "$failn" -eq 0 ]
