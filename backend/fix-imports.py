#!/usr/bin/env python3
"""
Fix logger imports and Blueprint statements
Script refactor accidentally broke imports and Blueprint calls
"""

import re
from pathlib import Path

def fix_file(filepath):
    """Fix a single file"""
    print(f"Fixing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix 1: Move logger import out of docstring
    # Pattern: """from core.logger import logger\n<actual docstring>"""
    content = re.sub(
        r'"""(\s*)from core\.logger import logger(\s+)(.*?)"""',
        r'"""\3"""\n\nfrom core.logger import logger',
        content,
        flags=re.DOTALL
    )

    # Fix 2: Fix Blueprint statements
    # Pattern: xxx_bp = Bluelogger.info('xxx', __name__)
    # Should be: xxx_bp = Blueprint('xxx', __name__)
    content = re.sub(
        r'(\w+)_bp = Bluelogger\.info\(',
        r'\1_bp = Blueprint(',
        content
    )

    if content != original:
        # Backup
        backup_path = filepath.with_suffix('.py.backup2')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)

        # Write fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ Fixed {filepath.name}")
        return True
    else:
        print(f"  ⏭️  No changes needed for {filepath.name}")
        return False

def main():
    """Fix all API files"""
    print("🔧 Fixing logger imports and Blueprint statements...")
    print("=" * 60)

    api_dir = Path('/home/user/S2RTool/backend/api')

    api_files = list(api_dir.glob('*.py'))
    api_files = [f for f in api_files if f.name != '__init__.py']

    fixed = 0
    for filepath in api_files:
        if fix_file(filepath):
            fixed += 1

    print("=" * 60)
    print(f"✅ Fixed {fixed} files")
    print("=" * 60)

if __name__ == "__main__":
    main()
