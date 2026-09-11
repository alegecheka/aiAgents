#!/usr/bin/env python3
"""
Repo Linter — enforces project directory structure with focus on test clarification.

Generic philosophy (per .ai/rules §5-§6): README.md is RECOMMENDED, not hard-required.
The directory structure itself must make it obvious which README to read first.
Works for ANY future project in projects/*, not just HOON — HOON is just the
current example. Session log stores are exempt.
Root README as Hub (§6 Generic): repo root README.md links to every
projects/<PROJECT>/README.md, to agents/README.md and to tools/README.md
(and tools/repo-linter); each project README links to its own part READMEs.
Linter warns if hub links are missing. agents/ is private — no file-count
limit, only 100 KB quota per agents/<specific-agent>/ (see .ai/rules §7 and
agents/README.md). tools/ is shared (formerly scripts/). Chat history: only
chat-history.<md|txt|html> (hyphen) — underscore is deprecated.
"""
import os
import sys

def _missing_hub_links(readme_path, required_substrings):
    """Return list of required substrings not found in readme_path, or [] if unreadable."""
    try:
        with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return required_substrings
    missing = [s for s in required_substrings if s not in content]
    return missing

def _find_descendant_readmes(proj_path, max_depth=2):
    """Find descendant README.md files within proj_path up to max_depth, relative to proj_path."""
    readmes = []
    for root, dirs, files in os.walk(proj_path):
        rel_root = os.path.relpath(root, proj_path)
        if rel_root == ".":
            continue
        depth = rel_root.count(os.sep) + 1  # +1 because rel_root is dir level
        if depth > max_depth:
            # prune deeper traversal
            dirs[:] = []
            continue
        if "README.md" in files:
            # normalize to posix-like for markdown link check
            rel = os.path.join(rel_root, "README.md").replace(os.sep, "/")
            readmes.append(rel)
    return sorted(readmes)

def check_structure(base_dir):
    errors = []
    warnings = []

    projects_root = os.path.join(base_dir, "projects")
    project_dirs = []
    if os.path.isdir(projects_root):
        project_dirs = [d for d in os.listdir(projects_root) if os.path.isdir(os.path.join(projects_root, d))]
    else:
        errors.append("projects/ missing — create at least one project like projects/HOON")
        project_dirs = []

    # --- repo root README hub check (generic) ---
    repo_readme = os.path.join(base_dir, "README.md")
    if os.path.exists(repo_readme):
        required_root_links = []
        for proj in sorted(project_dirs):
            required_root_links.append(f"projects/{proj}/README.md")
        # agents is private — only require link to its entry point README.md, not per-agent
        agents_entry = os.path.join(base_dir, "agents", "README.md")
        if os.path.exists(agents_entry):
            required_root_links.append("agents/README.md")
        # tools is shared (formerly scripts) — require links to its entry and key tools
        tools_entry = os.path.join(base_dir, "tools", "README.md")
        if os.path.exists(tools_entry):
            required_root_links.append("tools/README.md")
        tools_linter = os.path.join(base_dir, "tools", "repo-linter", "README.md")
        if os.path.exists(tools_linter):
            required_root_links.append("tools/repo-linter/README.md")
        if required_root_links:
            missing = _missing_hub_links(repo_readme, required_root_links)
            if missing:
                warnings.append(f"README.md missing hub links to: {', '.join(missing)} — add explicit markdown links to every project, agents/README.md and tools/README.md (see .ai/rules §6 Generic)")
        # For backward compat, also warn if HOON deep links missing when HOON exists (project hub already covers, but keep gentle warning)
        if "HOON" in project_dirs:
            hoon_deep = [
                "projects/HOON/spec-tests/README.md",
                "projects/HOON/implementations/c/README.md",
                "projects/HOON/implementations/cpp/README.md",
                "projects/HOON/implementations/python/README.md",
            ]
            existing_deep = [p for p in hoon_deep if os.path.exists(os.path.join(base_dir, p))]
            if existing_deep:
                missing_deep = _missing_hub_links(repo_readme, existing_deep)
                if missing_deep:
                    warnings.append(f"README.md missing HOON deep hub links to: {', '.join(missing_deep)} — repo root as hub should link to key sub-parts (see .ai/rules §6)")

    else:
        warnings.append("README.md missing at repo root — recommended as hub with links to all projects/*/README.md, agents/README.md and tools/README.md")

    if not project_dirs:
        warnings.append("projects/ has no subprojects — add at least one project (e.g., projects/HOON)")

    # --- per-project generic checks ---
    for proj in sorted(project_dirs):
        proj_path = os.path.join(projects_root, proj)
        proj_readme = os.path.join(proj_path, "README.md")
        if not os.path.exists(proj_readme):
            warnings.append(f"projects/{proj}/README.md missing — recommended as entry point (what {proj} is, how to build)")
            continue
        # hub: each project README should link to its descendant READMEs
        descendant = _find_descendant_readmes(proj_path, max_depth=2)
        docs_hoon = os.path.join(proj_path, "docs", "hoon.md")
        extra_expected = []
        if os.path.exists(docs_hoon):
            extra_expected.append("docs/hoon.md")
        required_proj_links = descendant + extra_expected
        if required_proj_links:
            missing = _missing_hub_links(proj_readme, required_proj_links)
            if missing:
                warnings.append(f"projects/{proj}/README.md missing hub links to: {', '.join(missing)} — add links to every part README inside that project (see .ai/rules §6)")

        # --- project-specific structure checks ---
        if proj == "HOON":
            spec = os.path.join(proj_path, "spec-tests")
            if not os.path.isdir(spec):
                errors.append("projects/HOON/spec-tests missing — universal tests not found")
            else:
                for d in ["valid", "invalid"]:
                    if not os.path.isdir(os.path.join(spec, d)):
                        errors.append(f"spec-tests/{d}/ missing — run 'valid/{{minimal,feature,integration}} + invalid/{{lexical,syntax,semantic}}' grouping")
                for sub in ["minimal", "feature", "integration"]:
                    p = os.path.join(spec, "valid", sub)
                    if not os.path.isdir(p):
                        errors.append(f"spec-tests/valid/{sub}/ missing — add minimal/feature/integration grouping")
                    elif not any(f.endswith(".hoon") for f in os.listdir(p)):
                        errors.append(f"spec-tests/valid/{sub}/ has no .hoon files — add at least one golden")
                for sub in ["lexical", "syntax", "semantic"]:
                    p = os.path.join(spec, "invalid", sub)
                    if not os.path.isdir(p):
                        errors.append(f"spec-tests/invalid/{sub}/ missing — categorize bad tests as lexical/syntax/semantic")
                    elif not any(f.endswith(".hoon") for f in os.listdir(p)):
                        errors.append(f"spec-tests/invalid/{sub}/ has no .hoon files")
                if not os.path.exists(os.path.join(spec, "README.md")):
                    warnings.append("spec-tests/README.md missing — recommended to explain valid/ vs invalid and --group usage")
                valid_expected = []
                for root, _, files in os.walk(os.path.join(spec, "valid")):
                    valid_expected.extend([f for f in files if f.endswith(".expected")])
                if not valid_expected:
                    errors.append("spec-tests/valid has no .expected dumps — each valid/*.hoon needs paired .expected")
                if os.path.isdir(os.path.join(spec, "bad")) and not os.path.isdir(os.path.join(spec, "invalid")):
                    warnings.append("spec-tests/bad/ exists but spec-tests/invalid/ missing — migrate to invalid/{lexical,syntax,semantic}")
            impl_root = os.path.join(proj_path, "implementations")
            if not os.path.isdir(impl_root):
                errors.append("projects/HOON/implementations/ missing")
            else:
                langs = [d for d in os.listdir(impl_root) if os.path.isdir(os.path.join(impl_root, d))]
                if not langs:
                    errors.append("implementations/ has no language subfolders (e.g., c, cpp, python)")
                for lang in langs:
                    lang_path = os.path.join(impl_root, lang)
                    has_test = any(os.path.exists(os.path.join(lang_path, f)) for f in ["Makefile", "CMakeLists.txt", "pyproject.toml", "tests/run-tests.sh"])
                    if not has_test:
                        warnings.append(f"implementations/{lang}/ has no Makefile/CMakeLists.txt/pyproject.toml — how to run tests?")
                    if not os.path.exists(os.path.join(lang_path, "README.md")):
                        warnings.append(f"implementations/{lang}/README.md missing — recommended (how to build that lang)")
        else:
            spec = os.path.join(proj_path, "spec-tests")
            if os.path.isdir(spec):
                if not os.path.exists(os.path.join(spec, "README.md")):
                    warnings.append(f"projects/{proj}/spec-tests/README.md missing — recommended to explain test layout")
                subdirs = [d for d in os.listdir(spec) if os.path.isdir(os.path.join(spec, d))]
                if len(subdirs) < 1:
                    warnings.append(f"projects/{proj}/spec-tests/ looks flat — split into groups (e.g., valid/invalid) for clarity")
                valid_path = os.path.join(spec, "valid")
                if os.path.isdir(valid_path):
                    has_expected = False
                    for _, _, files in os.walk(valid_path):
                        if any(f.endswith(".expected") for f in files):
                            has_expected = True
                            break
                    if not has_expected:
                        warnings.append(f"projects/{proj}/spec-tests/valid has no .expected dumps — add expected outputs for valid tests")
            impl_root = os.path.join(proj_path, "implementations")
            if os.path.isdir(impl_root):
                langs = [d for d in os.listdir(impl_root) if os.path.isdir(os.path.join(impl_root, d))]
                for lang in langs:
                    lang_path = os.path.join(impl_root, lang)
                    has_test = any(os.path.exists(os.path.join(lang_path, f)) for f in ["Makefile", "CMakeLists.txt", "pyproject.toml", "tests/run-tests.sh", "build.gradle", "Cargo.toml"])
                    if not has_test:
                        warnings.append(f"projects/{proj}/implementations/{lang}/ has no build/test entry (Makefile/CMakeLists.txt/pyproject.toml) — how to run tests?")
                    if not os.path.exists(os.path.join(lang_path, "README.md")):
                        warnings.append(f"projects/{proj}/implementations/{lang}/README.md missing — recommended (how to build that lang)")

    # --- agents: private workspace, no file-count limit, 100 KB quota ---
    agents_root = os.path.join(base_dir, "agents")
    if os.path.isdir(agents_root):
        agents_readme = os.path.join(agents_root, "README.md")
        if not os.path.exists(agents_readme):
            warnings.append("agents/README.md missing — add description of what agents/ is and why we use it (private place + best-practices library, human as manager)")
        # Per-agent 100 KB quota (no file-count limit) — see .ai/rules §7
        for item in os.listdir(agents_root):
            item_path = os.path.join(agents_root, item)
            if not os.path.isdir(item_path):
                continue
            total = 0
            for root, _, files in os.walk(item_path):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        total += os.path.getsize(fpath)
                    except OSError:
                        pass
            if total > 100 * 1024:
                warnings.append(f"agents/{item}/ exceeds 100 KB quota ({total} bytes > 102400) — keep lean, no file-count limit but stay under 100 KB (see .ai/rules §7)")
        # Note: individual agents may use any style; no per-agent README or code checks.
        # The linter intentionally does not enforce chat-history.* here — see .ai/rules §7 for convention, not enforcement.

    return errors, warnings

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    print(f"🤖 repo-linter (tools) waking up... inspecting {repo_root}")
    
    errors, warnings = check_structure(repo_root)
    
    for w in warnings:
        print(f"⚠️  {w}")

    if errors:
        print("❌ I found structural violations:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
        
    if warnings:
        print("✅ Structure is tidy (with recommendations above)")
    else:
        print("✅ All house rules observed. The repository is tidy!")
    sys.exit(0)
