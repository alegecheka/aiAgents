#!/usr/bin/env bash
# HOON parser test suite (Python implementation).
#   Groups: valid/minimal, valid/feature, valid/integration, invalid/lexical, invalid/syntax, invalid/semantic
#   Run all: ./run-tests.sh  or  PYTHONPATH=src ./run-tests.sh --group=valid/feature
set -u

root="$(cd "$(dirname "$0")/.." && pwd)"
spec="$(cd "$root/../../spec-tests" && pwd)"
bin="$root/tools/hoon-parse"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

GROUP=""
if [[ "${1:-}" == --group=* ]]; then
    GROUP="${1#--group=}"
    if [[ "$GROUP" == "bad" || "$GROUP" == bad/* ]]; then
        GROUP="${GROUP/bad/invalid}"
    fi
    echo "🔍 Running group: $GROUP"
fi

pass=0; failn=0
ok()   { printf 'PASS  %s\n' "$1"; pass=$((pass + 1)); }
bad()  { printf 'FAIL  %s\n' "$1"; failn=$((failn + 1)); }

# helper to run hoon-parse with correct PYTHONPATH
run_bin() {
    PYTHONPATH="$root/src" "$bin" "$@"
}

# --- golden tests (valid) ------------------------------------------------
found_golden=0
while IFS= read -r -d '' exp; do
    if [[ -n "$GROUP" ]]; then
        if [[ "$exp" != *"$GROUP"* ]]; then
            if [[ "$GROUP" == invalid* ]]; then
                continue
            fi
            continue
        fi
    else
        if [[ "$exp" == *"/invalid/"* ]]; then continue; fi
    fi
    found_golden=1
    hoon="${exp%.expected}.hoon"
    base="$(basename "$exp" .expected)"
    rel="${exp#$spec/}"
    rel="${rel%.expected}"
    if [ ! -f "$hoon" ]; then
        bad "$rel: missing .hoon for .expected"
        continue
    fi
    if run_bin "$hoon" > "$tmp/$base.out" 2> "$tmp/$base.err"; then
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
    if [[ -n "${seen_bad[$name]:-}" ]]; then
        continue
    fi
    seen_bad[$name]=1
    if [[ -n "$GROUP" ]]; then
        if [[ "$GROUP" == valid* ]]; then
            continue
        fi
        if [[ "$f" != *"$GROUP"* && "$name" != *"$GROUP"* ]]; then
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
    if run_bin "$f" > /dev/null 2>&1; then
        bad "$rel: parser ACCEPTED it (expected rejection)"
    else
        ok "$rel: rejected as expected"
    fi
done

if [ "$found_invalid" -eq 0 ]; then
    if [[ -n "$GROUP" && "$GROUP" == valid* ]]; then
        :
    else
        if [[ -n "$GROUP" ]]; then
            bad "no invalid files found for group '$GROUP'"
        fi
    fi
fi

printf "\n%d passed, %d failed\n" "$pass" "$failn"
[ "$failn" -eq 0 ]
