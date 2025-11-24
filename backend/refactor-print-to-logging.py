#!/usr/bin/env python3
"""
Refactor Script: Replace print() with logging statements
Converts print() calls to appropriate logging levels based on content
"""

import re
import os
from pathlib import Path

# Patterns to detect log levels
PATTERNS = {
    'error': re.compile(r'(error|failed|exception|❌|⚠️)', re.IGNORECASE),
    'warning': re.compile(r'(warning|warn|⚠️|skipping|deprecated)', re.IGNORECASE),
    'info': re.compile(r'(✅|✓|info|success|complete|done|ready|loaded|processing|saved)', re.IGNORECASE),
    'debug': re.compile(r'(debug|🔍|analyzing|checking|validating)', re.IGNORECASE),
}

def detect_log_level(content: str) -> str:
    """Detect appropriate log level from print content"""
    content_lower = content.lower()

    if PATTERNS['error'].search(content_lower):
        return 'error'
    elif PATTERNS['warning'].search(content_lower):
        return 'warning'
    elif PATTERNS['debug'].search(content_lower):
        return 'debug'
    else:
        return 'info'

def convert_print_to_logging(line: str) -> str:
    """Convert a print() line to logging statement"""
    # Match print(...) patterns
    print_pattern = r'print\((.*?)\)(?:\s*#.*)?$'
    match = re.search(print_pattern, line)

    if not match:
        return line

    content = match.group(1).strip()

    # Detect log level
    level = detect_log_level(content)

    # Replace print with logger
    new_line = line.replace(f'print({content})', f'logger.{level}({content})')

    return new_line

def process_file(filepath: Path, dry_run: bool = False):
    """Process a single Python file"""
    print(f"📝 Processing {filepath.relative_to(Path.cwd())}...")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        new_lines = []
        needs_import = False

        for line in lines:
            if 'print(' in line and not line.strip().startswith('#'):
                new_line = convert_print_to_logging(line)
                if new_line != line:
                    modified = True
                    needs_import = True
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        if modified and not dry_run:
            # Backup original
            backup_path = filepath.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            # Add import if needed
            if needs_import and 'from core.logger import logger' not in ''.join(new_lines):
                # Find where to insert import (after docstring/comments)
                insert_idx = 0
                for i, line in enumerate(new_lines):
                    if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                        insert_idx = i
                        break

                new_lines.insert(insert_idx, 'from core.logger import logger\n')

            # Write modified file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            print(f"✅ Modified {filepath.name}")
        elif modified:
            print(f"🔍 Would modify {filepath.name} (dry run)")
        else:
            print(f"⏭️  No changes needed for {filepath.name}")

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

def main():
    """Main refactor function"""
    print("🚀 Backend Logging Refactor Tool")
    print("=" * 60)
    print()

    # Find all Python files in api/ and core/
    backend_dir = Path(__file__).parent
    api_dir = backend_dir / 'api'
    core_dir = backend_dir / 'core'

    py_files = []
    if api_dir.exists():
        py_files.extend(list(api_dir.glob('*.py')))
    if core_dir.exists():
        py_files.extend([f for f in core_dir.glob('*.py') if f.name != 'logger.py'])

    print(f"Found {len(py_files)} Python files to process")
    print()

    dry_run = input("Dry run first? (y/n): ").lower() == 'y'
    print()

    for filepath in py_files:
        if filepath.name != '__init__.py':
            process_file(filepath, dry_run=dry_run)

    print()
    print("=" * 60)
    if dry_run:
        print("✅ Dry run complete! Run again with 'n' to apply changes.")
    else:
        print("✅ Refactoring complete!")
        print()
        print("Next steps:")
        print("1. Review changes: git diff backend/")
        print("2. Test all API endpoints")
        print("3. Remove .backup files if satisfied")
        print("4. Commit: git add backend/ && git commit")
    print("=" * 60)

if __name__ == "__main__":
    main()
