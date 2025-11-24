#!/usr/bin/env python3
"""
Remove duplicate utility functions from script files
These functions are now in utils.js and should not be redefined
"""

import re
from pathlib import Path

# Functions to remove (they're in utils.js)
FUNCTIONS_TO_REMOVE = [
    'optimizeImageForUpload',
    'showError',
    'showSuccess',
    'hideMessage',
    'showSpinner',
]

def remove_function(content, func_name):
    """Remove a function definition from content"""
    # Pattern: function declaration to next function or end
    patterns = [
        # async function name(...) { ... }
        rf'async function {func_name}\([^)]*\)\s*{{[^}}]*}}',
        # function name(...) { ... }
        rf'function {func_name}\([^)]*\)\s*{{[^}}]*}}',
    ]

    for pattern in patterns:
        # Find all matches
        matches = list(re.finditer(pattern, content, re.DOTALL))
        if matches:
            # Remove from end to start to preserve positions
            for match in reversed(matches):
                start = match.start()
                end = match.end()

                # Find the actual end including nested braces
                brace_count = 0
                in_function = False
                actual_end = start

                i = start
                while i < len(content):
                    if content[i] == '{':
                        brace_count += 1
                        in_function = True
                    elif content[i] == '}':
                        brace_count -= 1
                        if in_function and brace_count == 0:
                            actual_end = i + 1
                            break
                    i += 1

                # Remove the function
                if actual_end > start:
                    # Also remove trailing newlines
                    while actual_end < len(content) and content[actual_end] in '\n\r':
                        actual_end += 1
                    content = content[:start] + content[actual_end:]

    return content

def clean_file(filepath):
    """Remove duplicate functions from a file"""
    print(f"Cleaning {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    for func_name in FUNCTIONS_TO_REMOVE:
        content = remove_function(content, func_name)

    # Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)

    if content != original:
        # Backup
        backup_path = filepath.with_suffix('.js.backup3')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)

        # Write cleaned content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ Removed duplicate functions from {filepath.name}")
        return True
    else:
        print(f"  ⏭️  No duplicates found in {filepath.name}")
        return False

def main():
    """Clean all script files"""
    print("🧹 Removing duplicate utility functions...")
    print("=" * 60)

    frontend_dir = Path('/home/user/S2RTool/frontend')

    script_files = [
        'building-script.js',
        'script.js',
        'planning-script.js',
        'planning-detail-script.js',
    ]

    cleaned = 0
    for filename in script_files:
        filepath = frontend_dir / filename
        if filepath.exists():
            if clean_file(filepath):
                cleaned += 1

    print("=" * 60)
    print(f"✅ Cleaned {cleaned} files")
    print("")
    print("Functions now only in utils.js (no duplicates):")
    for func in FUNCTIONS_TO_REMOVE:
        print(f"  - {func}()")
    print("=" * 60)

if __name__ == "__main__":
    main()
