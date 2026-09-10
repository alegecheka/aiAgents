#!/usr/bin/env python3
"""
Repo Linter — enforces project directory structure with focus on test clarification.

New philosophy (per .ai/rules §6): README.md is RECOMMENDED, not hard-required.
The directory structure itself must make it obvious which README to read first:
  - projects/HOON/README.md → entry point
  - projects/HOON/spec-tests/README.md → test layout
  - projects/HOON/implementations/<lang>/README.md → language
We enforce STRUCTURE, not README count. Session log stores are exempt.
Root README as Hub (§6): repo root README.md and projects/HOON/README.md must
link to their part READMEs — linter warns if hub links are missing.
Chat history: only chat-history.<md|txt|html> (hyphen) — underscore is deprecated.
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

def check_structure(base_dir):
    errors = []
    warnings = []

    # --- repo root README hub check ---
    repo_readme = os.path.join(base_dir, "README.md")
    if os.path.exists(repo_readme):
        # per §6 Root README as Hub — repo root must link to its parts
        required_root_links = [
            "projects/HOON/README.md",
            "projects/HOON/spec-tests/README.md",
            "projects/HOON/implementations/c/README.md",
            "projects/HOON/implementations/cpp/README.md",
            "projects/HOON/implementations/python/README.md",
            "agents/repo-linter/README.md",
        ]
        missing = _missing_hub_links(repo_readme, required_root_links)
        if missing:
            warnings.append(f"README.md missing hub links to: {', '.join(missing)} — add explicit markdown links to every part README (see .ai/rules §6)")
    else:
        warnings.append("README.md missing at repo root — recommended as hub with links to all part READMEs")

    # --- projects/HOON structure ---
    hoon = os.path.join(base_dir, "projects", "HOON")
    if not os.path.isdir(hoon):
        errors.append("projects/HOON missing — main project not found")
        return errors, warnings

    # Entry point README is recommended, not required — warn if missing
    hoon_readme = os.path.join(hoon, "README.md")
    if not os.path.exists(hoon_readme):
        warnings.append("projects/HOON/README.md missing — recommended as entry point (what HOON is, how to build any lang)")
    else:
        required_hoon_links = [
            "spec-tests/README.md",
            "implementations/c/README.md",
            "implementations/cpp/README.md",
            "implementations/python/README.md",
        ]
        missing = _missing_hub_links(hoon_readme, required_hoon_links)
        if missing:
            warnings.append(f"projects/HOON/README.md missing hub links to: {', '.join(missing)} — add links to spec-tests and each implementations/<lang>/README.md (see .ai/rules §6)")

    # spec-tests must exist and be clearly grouped
    spec = os.path.join(hoon, "spec-tests")
    if not os.path.isdir(spec):
        errors.append("projects/HOON/spec-tests missing — universal tests not found")
    else:
        # Must have valid/ and invalid/ (not just flat bad/)
        for d in ["valid", "invalid"]:
            if not os.path.isdir(os.path.join(spec, d)):
                errors.append(f"spec-tests/{d}/ missing — run 'valid/{{minimal,feature,integration}} + invalid/{{lexical,syntax,semantic}}' grouping")

        # valid sub-groups
        for sub in ["minimal", "feature", "integration"]:
            p = os.path.join(spec, "valid", sub)
            if not os.path.isdir(p):
                errors.append(f"spec-tests/valid/{sub}/ missing — add minimal/feature/integration grouping")
            elif not any(f.endswith(".hoon") for f in os.listdir(p)):
                errors.append(f"spec-tests/valid/{sub}/ has no .hoon files — add at least one golden")

        # invalid sub-groups
        for sub in ["lexical", "syntax", "semantic"]:
            p = os.path.join(spec, "invalid", sub)
            if not os.path.isdir(p):
                errors.append(f"spec-tests/invalid/{sub}/ missing — categorize bad tests as lexical/syntax/semantic")
            elif not any(f.endswith(".hoon") for f in os.listdir(p)):
                errors.append(f"spec-tests/invalid/{sub}/ has no .hoon files")

        # spec-tests/README.md is the test-clarification entry point — recommended
        if not os.path.exists(os.path.join(spec, "README.md")):
            warnings.append("spec-tests/README.md missing — recommended to explain valid/ vs invalid and --group usage")

        # valid must have .expected dumps
        valid_expected = []
        for root, _, files in os.walk(os.path.join(spec, "valid")):
            valid_expected.extend([f for f in files if f.endswith(".expected")])
        if not valid_expected:
            errors.append("spec-tests/valid has no .expected dumps — each valid/*.hoon needs paired .expected")

        # legacy bad/ is allowed as alias, but invalid/ is the source of truth
        if os.path.isdir(os.path.join(spec, "bad")) and not os.path.isdir(os.path.join(spec, "invalid")):
            warnings.append("spec-tests/bad/ exists but spec-tests/invalid/ missing — migrate to invalid/{lexical,syntax,semantic}")

    # implementations
    impl_root = os.path.join(hoon, "implementations")
    if not os.path.isdir(impl_root):
        errors.append("projects/HOON/implementations/ missing")
    else:
        langs = [d for d in os.listdir(impl_root) if os.path.isdir(os.path.join(impl_root, d))]
        if not langs:
            errors.append("implementations/ has no language subfolders (e.g., c, cpp, python)")
        for lang in langs:
            lang_path = os.path.join(impl_root, lang)
            # each lang should have a way to test — Makefile or CMakeLists.txt or pyproject.toml
            has_test = any(os.path.exists(os.path.join(lang_path, f)) for f in ["Makefile", "CMakeLists.txt", "pyproject.toml", "tests/run-tests.sh"])
            if not has_test:
                warnings.append(f"implementations/{lang}/ has no Makefile/CMakeLists.txt/pyproject.toml — how to run tests?")
            # README is recommended per lang, not required
            if not os.path.exists(os.path.join(lang_path, "README.md")):
                warnings.append(f"implementations/{lang}/README.md missing — recommended (how to build that lang)")

    # --- agents structure ---
    agents_root = os.path.join(base_dir, "agents")
    if os.path.isdir(agents_root):
        for item in os.listdir(agents_root):
            item_path = os.path.join(agents_root, item)
            if not os.path.isdir(item_path):
                continue
            is_session = "session" in item.lower()
            has_hyphen = any(os.path.exists(os.path.join(item_path, f"chat-history.{ext}")) for ext in ["md", "txt", "html"])
            has_underscore = any(os.path.exists(os.path.join(item_path, f"chat_history.{ext}")) for ext in ["md", "txt", "html"])
            has_any = has_hyphen or has_underscore
            if is_session or has_any:
                if has_underscore:
                    errors.append(f"Session log {item} has deprecated chat_history.* (underscore) — remove duplicate, keep only chat-history.* (hyphen)")
                if not has_hyphen:
                    errors.append(f"Session log {item} must contain chat-history.<md|txt|html> (hyphen) — chat_history.* underscore is deprecated")
                # session folders must NOT be required to have README — they are log stores
                continue
            # Non-session agents: README is RECOMMENDED, not hard error, but warn
            if not os.path.exists(os.path.join(item_path, "README.md")):
                warnings.append(f"agents/{item}/README.md missing — recommended to explain what the agent does")
            # must have some code
            try:
                has_code = any(f.endswith(".py") or f.endswith(".sh") for f in os.listdir(item_path))
            except Exception:
                has_code = False
            if not has_code and item != "README.md":
                warnings.append(f"agents/{item}/ has no .py/.sh — is it an empty agent?")

    return errors, warnings

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    print(f"🤖 repo-linter agent waking up... inspecting {repo_root}")
    
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
