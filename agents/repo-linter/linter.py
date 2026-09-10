#!/usr/bin/env python3
import os
import sys

def check_structure(base_dir):
    errors = []
    
    # Enforce house rule: One top-level project/agent = one directory = one README
    # Session log stores (agents/*session* with chat-history.*) are exempt — they are
    # log stores per .ai/rules §7, not projects: they must have chat-history.<ext>
    # and may have up to 9 additional useful files, not a boilerplate README.
    for folder in ['projects', 'agents']:
        target_dir = os.path.join(base_dir, folder)
        if not os.path.exists(target_dir):
            continue
            
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            # We skip files in the root of 'agents/' or 'projects/', we only look at subdirectories
            if os.path.isdir(item_path):
                # Exempt session log stores
                is_session = "session" in item.lower()
                has_history = any(
                    os.path.exists(os.path.join(item_path, f"chat-history.{ext}")) or
                    os.path.exists(os.path.join(item_path, f"chat_history.{ext}"))
                    for ext in ["md", "txt", "html"]
                )
                if is_session or has_history:
                    # Must have a chat-history file, but not a README
                    if not has_history:
                        errors.append(f"[Violation] Session log {folder}/{item} must contain chat-history.<md|txt|html> (or legacy chat_history.*)")
                    continue
                readme_path = os.path.join(item_path, 'README.md')
                if not os.path.exists(readme_path):
                    errors.append(f"[Violation] House rules dictate {folder}/{item} needs a README.md")
    
    return errors

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    print(f"🤖 repo-linter agent waking up... inspecting {repo_root}")
    
    errors = check_structure(repo_root)
    
    if errors:
        print("❌ I found some violations of our house rules:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
        
    print("✅ All house rules observed. The repository is tidy!")
    sys.exit(0)
