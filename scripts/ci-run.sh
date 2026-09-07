#!/usr/bin/env bash
set -euo pipefail

# Find the repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "======================================"
echo "🤖 Starting CI orchestration script..."
echo "======================================"

echo ""
echo "==> 1. Running repo-linter agent..."
if ! "$REPO_ROOT/agents/repo-linter/linter.py"; then
    echo "❌ repo-linter agent failed! Please fix the errors above."
    exit 1
fi

echo ""
echo "==> 2. Running project tests..."
for project_dir in "$REPO_ROOT"/projects/*/; do
    if [ -d "$project_dir" ]; then
        project_name=$(basename "$project_dir")
        if [ -f "$project_dir/Makefile" ]; then
            echo "--> Testing project: $project_name"
            make -C "$project_dir" test
        else
            echo "--> Skipping $project_name (no Makefile found)"
        fi
    fi
done

echo ""
echo "✅ CI Completed Successfully! Agents are happy."
