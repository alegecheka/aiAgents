#!/usr/bin/env bash
set -euo pipefail

# Find the repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "======================================"
echo "🤖 Starting CI orchestration script..."
echo "======================================"

echo ""
echo "==> 1. Running repo-linter (tools/)..."
if ! "$REPO_ROOT/tools/repo-linter/linter.py"; then
    echo "❌ repo-linter failed! Please fix the errors above."
    exit 1
fi

echo ""
echo "==> 2. Running project tests..."

# Iterate through every folder inside the implementations directory of HOON
for impl_dir in "$REPO_ROOT"/projects/HOON/implementations/*/; do
    if [ -d "$impl_dir" ]; then
        impl_name=$(basename "$impl_dir")
        echo "--> Testing HOON Implementation: $impl_name"
        
        # Prefer CMake if available (for C++)
        if [ -f "$impl_dir/CMakeLists.txt" ] && command -v cmake >/dev/null 2>&1; then
            echo "    (Using CMake)"
            (
                cd "$impl_dir"
                cmake -B build >/dev/null
                cmake --build build >/dev/null
                cd build && ctest --output-on-failure
            )
        # Fallback to Makefile (for C and fallback C++)
        elif [ -f "$impl_dir/Makefile" ]; then
            echo "    (Using Makefile)"
            make -C "$impl_dir" test
        else
            echo "--> Skipping $impl_name (no Makefile or CMakeLists.txt found)"
        fi
    fi
done

echo ""
echo "✅ CI Completed Successfully! Agents are happy."
