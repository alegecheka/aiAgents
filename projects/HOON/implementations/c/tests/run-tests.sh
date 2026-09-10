#!/usr/bin/env bash
# HOON parser test suite (C implementation).
#   Groups:
#     valid/minimal     — smallest legal docs
#     valid/feature     — isolated feature (numbers, strings, texts, keys, arrays, objects, comments, scalars)
#     valid/integration — combined torture/mega/complex
#     invalid/lexical   — token errors (bad escapes, unterminated)
#     invalid/syntax    — grammar errors (missing colon/semi, bad numbers, double braces)
#     invalid/semantic  — meaning errors (duplicate keys, bare words)
#   Run all: ./run-tests.sh
#   Run subgroup: ./run-tests.sh --group=valid/feature  or --group=invalid/semantic  or --group=valid/minimal
set -u

root="$(cd "$(dirname "$0")/.." && pwd)"
spec="$(cd "$root/../../spec-tests" && pwd)"
bin="$root/${BUILD:-build}/hoon-parse"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

GROUP=""
if [[ "${1:-}" == --group=* ]]; then
    GROUP="${1#--group=}"
    # alias: bad -> invalid
    if [[ "$GROUP" == "bad" || "$GROUP" == bad/* ]]; then
        GROUP="${GROUP/bad/invalid}"
    fi
    echo "🔍 Running group: $GROUP"
fi

pass=0; failn=0
ok()   { printf 'PASS  %s\n' "$1"; pass=$((pass + 1)); }
bad()  { printf 'FAIL  %s\n' "$1"; failn=$((failn + 1)); }

# --- golden tests (valid) ------------------------------------------------
found_golden=0
# find all *.expected recursively under spec (covers valid/minimal, feature, integration and legacy root)
while IFS= read -r -d '' exp; do
    # group filter
    if [[ -n "$GROUP" ]]; then
        if [[ "$exp" != *"$GROUP"* ]]; then
            # if group is invalid/*, skip all valid goldens entirely
            if [[ "$GROUP" == invalid* ]]; then
                continue
            fi
            # if group is valid/* but exp not in that subpath, skip
            continue
        fi
    else
        # no group -> only consider valid goldens (skip any stray expected in invalid)
        if [[ "$exp" == *"/invalid/"* ]]; then continue; fi
    fi
    found_golden=1
    # derive hoon path: replace .expected with .hoon
    hoon="${exp%.expected}.hoon"
    base="$(basename "$exp" .expected)"
    # pretty name: relative to spec
    rel="${exp#$spec/}"
    rel="${rel%.expected}"
    if [ ! -f "$hoon" ]; then
        bad "$rel: missing .hoon for .expected"
        continue
    fi
    if "$bin" "$hoon" > "$tmp/$base.out" 2> "$tmp/$base.err"; then
        if diff -u "$exp" "$tmp/$base.out" > "$tmp/$base.diff"; then
            ok "$rel.hoon parses; golden dump matches"
        else
            bad "$rel.hoon: dump differs from golden (diff below)"
            sed 's/^/    /' "$tmp/$base.diff" | head -60
        fi
    else
        bad "$rel.hoon: parser rejected it (expected success)"
        sed 's/^/    /' "$tmp/$base.err" | head -10
    fi
done < <(find "$spec" -type f -name "*.expected" -print0 | sort -z)

if [ "$found_golden" -eq 0 ]; then
    if [[ -n "$GROUP" && ( "$GROUP" == invalid* || "$GROUP" == lexical || "$GROUP" == syntax || "$GROUP" == semantic || "$GROUP" == "bad" || "$GROUP" == bad/* ) ]]; then
        : # no goldens expected for invalid-only group
    else
        bad "no golden files found for group '${GROUP:-all}' in $spec"
    fi
fi

# --- negative tests (invalid) --------------------------------------------
# collect all invalid .hoon files from both new hierarchy and legacy bad/ alias, dedup by basename
declare -A seen_bad
found_invalid=0
# gather candidates - prefer new hierarchy (invalid/) over legacy alias (bad/) for dedup
candidates=()
while IFS= read -r -d '' f; do
    candidates+=("$f")
done < <(find "$spec/invalid" -type f -name "*.hoon" -print0 2>/dev/null | sort -z)
while IFS= read -r -d '' f; do
    candidates+=("$f")
done < <(find "$spec/bad" -type f -name "*.hoon" -print0 2>/dev/null | sort -z)

for f in "${candidates[@]}"; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    # dedup by basename (alias period: same file appears in both bad/ and invalid/)
    if [[ -n "${seen_bad[$name]:-}" ]]; then
        continue
    fi
    seen_bad[$name]=1

    # group filter for invalid
    if [[ -n "$GROUP" ]]; then
        # if group is valid/*, skip all invalid
        if [[ "$GROUP" == valid* ]]; then
            continue
        fi
        if [[ "$f" != *"$GROUP"* && "$name" != *"$GROUP"* ]]; then
            # also handle bare group names like "lexical" without prefix
            if [[ "$GROUP" != "lexical" && "$GROUP" != "syntax" && "$GROUP" != "semantic" ]]; then
                continue
            fi
            if [[ "$f" != *"$GROUP"* ]]; then
                continue
            fi
        fi
    fi

    found_invalid=1
    rel="${f#$spec/}"
    if "$bin" "$f" > /dev/null 2>&1; then
        bad "$rel: parser ACCEPTED it (expected rejection)"
    else
        ok "$rel: rejected as expected"
    fi
done

if [ "$found_invalid" -eq 0 ]; then
    if [[ -n "$GROUP" && "$GROUP" == valid* ]]; then
        : # no invalid expected for valid-only group
    else
        # only warn if group was invalid and nothing found
        if [[ -n "$GROUP" ]]; then
            bad "no invalid files found for group '$GROUP'"
        fi
    fi
fi

printf "\n%d passed, %d failed\n" "$pass" "$failn"
[ "$failn" -eq 0 ]
