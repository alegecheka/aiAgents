#!/usr/bin/env python3
import os
import sys

def check_structure(base_dir):
    errors = []
    
    # Enforce house rule: One project/agent = one directory = one README
    for folder in ['projects', 'agents']:
        target_dir = os.path.join(base_dir, folder)
        if not os.path.exists(target_dir):
            continue
            
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            # We skip files in the root of 'agents/' or 'projects/', we only look at subdirectories
            if os.path.isdir(item_path):
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
